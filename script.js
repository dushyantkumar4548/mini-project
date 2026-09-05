/**
 * PERSONAL EXPENSE TRACKER - JAVASCRIPT CONTROLLER
 * HTML5 + CSS3 + JavaScript + Python Flask
 */

// --- Global State ---
let isBackendConnected = false;
let expensesList = [];
let categoryChartInstance = null;
let monthlyChartInstance = null;

const STORAGE_KEY = 'college_expense_tracker_data';
const BUDGET_KEY = 'college_expense_monthly_budget';

const CATEGORY_COLORS = {
  Food: '#f59e0b',
  Travel: '#0ea5e9',
  Shopping: '#a855f7',
  Education: '#3b82f6',
  Bills: '#ef4444',
  Entertainment: '#ec4899',
  Health: '#10b981',
  Other: '#64748b',
};

// --- DOM Elements ---
const form = document.getElementById('expenseForm');
const categoryInput = document.getElementById('category');
const descriptionInput = document.getElementById('description');
const amountInput = document.getElementById('amount');
const dateInput = document.getElementById('date');

const tableBody = document.getElementById('expenseTableBody');
const totalAmountEl = document.getElementById('totalAmount');
const transactionCountEl = document.getElementById('transactionCount');
const tableSummaryText = document.getElementById('tableSummaryText');

const monthlyBudgetInput = document.getElementById('monthlyBudget');
const budgetProgressBar = document.getElementById('budgetProgressBar');
const budgetStatusText = document.getElementById('budgetStatusText');
const budgetSpentEl = document.getElementById('budgetSpent');
const budgetRemainingEl = document.getElementById('budgetRemaining');

const searchBox = document.getElementById('searchBox');
const categoryFilter = document.getElementById('categoryFilter');
const sortBy = document.getElementById('sortBy');

const exportCsvBtn = document.getElementById('exportCsvBtn');
const clearDataBtn = document.getElementById('clearDataBtn');

const doughnutTabBtn = document.getElementById('doughnutTabBtn');
const barTabBtn = document.getElementById('barTabBtn');
const categoryCanvas = document.getElementById('categoryChart');
const monthlyCanvas = document.getElementById('monthlyChart');

// --- Helper: Format Indian Rupee Currency ---
function formatINR(val) {
  const num = Number(val) || 0;
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 2,
  }).format(num);
}

// --- Helper: Toast Notification ---
function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;

  const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
  toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3200);
}

// --- Helper: Default Today's Date ---
function getTodayDate() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

// --- Local Storage Management ---
function getLocalExpenses() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    return [];
  }
}

function saveLocalExpenses(data) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

// --- Backend Connection & Data Loading ---
async function checkBackendConnection() {
  try {
    const res = await fetch('/api/expenses', { method: 'GET', cache: 'no-cache' });
    if (res.ok) {
      const json = await res.json();
      isBackendConnected = true;
      expensesList = json.expenses || [];
      return true;
    }
  } catch (err) {
    // Backend not running, fallback to localStorage
  }

  isBackendConnected = false;
  expensesList = getLocalExpenses();
  return false;
}

async function loadData() {
  if (isBackendConnected) {
    try {
      const res = await fetch('/api/expenses');
      const json = await res.json();
      expensesList = json.expenses || [];
    } catch (e) {
      expensesList = getLocalExpenses();
    }
  } else {
    expensesList = getLocalExpenses();
  }
  applyFiltersAndRender();
}

// --- Budget Logic ---
function updateBudgetMonitor() {
  const budget = parseFloat(monthlyBudgetInput.value) || 0;
  const currentMonth = getTodayDate().slice(0, 7);

  const thisMonthSpent = expensesList
    .filter((e) => (e.date || '').startsWith(currentMonth))
    .reduce((sum, e) => sum + (parseFloat(e.amount) || 0), 0);

  budgetSpentEl.textContent = `Spent this month: ${formatINR(thisMonthSpent)}`;

  const remaining = budget - thisMonthSpent;
  budgetRemainingEl.textContent = `Remaining: ${formatINR(remaining)}`;

  let percentage = budget > 0 ? (thisMonthSpent / budget) * 100 : 0;
  budgetProgressBar.style.width = `${Math.min(percentage, 100)}%`;

  if (percentage >= 100) {
    budgetProgressBar.style.backgroundColor = 'var(--danger)';
    budgetStatusText.textContent = `⚠️ Warning: You have exceeded your monthly budget by ${formatINR(
      Math.abs(remaining)
    )}!`;
    budgetStatusText.style.color = 'var(--danger)';
  } else if (percentage >= 80) {
    budgetProgressBar.style.backgroundColor = 'var(--warning)';
    budgetStatusText.textContent = `⚡ Alert: You have used ${percentage.toFixed(
      1
    )}% of your monthly budget.`;
    budgetStatusText.style.color = 'var(--warning)';
  } else {
    budgetProgressBar.style.backgroundColor = 'var(--success)';
    budgetStatusText.textContent = `You have utilized ${percentage.toFixed(
      1
    )}% of your monthly budget.`;
    budgetStatusText.style.color = 'var(--text-muted)';
  }

  localStorage.setItem(BUDGET_KEY, String(budget));
}

// --- Chart.js Rendering ---
function renderCharts() {
  if (typeof Chart === 'undefined') return;

  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const textColor = isDark ? '#f8fafc' : '#1e293b';

  // 1. Category Breakdown (Doughnut)
  const categoryTotals = {};
  expensesList.forEach((e) => {
    const cat = e.category || 'Other';
    categoryTotals[cat] = (categoryTotals[cat] || 0) + parseFloat(e.amount || 0);
  });

  const categories = Object.keys(categoryTotals);
  const amounts = Object.values(categoryTotals);
  const bgColors = categories.map((c) => CATEGORY_COLORS[c] || '#64748b');

  if (categoryChartInstance) {
    categoryChartInstance.destroy();
  }

  if (categories.length > 0) {
    categoryChartInstance = new Chart(categoryCanvas, {
      type: 'doughnut',
      data: {
        labels: categories,
        datasets: [
          {
            data: amounts,
            backgroundColor: bgColors,
            borderColor: isDark ? '#1e293b' : '#ffffff',
            borderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { color: textColor, font: { family: 'Inter', size: 12 } },
          },
          tooltip: {
            callbacks: {
              label: (ctx) => ` ${ctx.label}: ${formatINR(ctx.raw)}`,
            },
          },
        },
      },
    });
  }

  // 2. Monthly Trend (Bar Chart)
  const monthlyTotals = {};
  expensesList.forEach((e) => {
    const month = (e.date || '').slice(0, 7) || 'Unknown';
    monthlyTotals[month] = (monthlyTotals[month] || 0) + parseFloat(e.amount || 0);
  });

  const months = Object.keys(monthlyTotals).sort();
  const monthAmounts = months.map((m) => monthlyTotals[m]);

  if (monthlyChartInstance) {
    monthlyChartInstance.destroy();
  }

  if (months.length > 0) {
    monthlyChartInstance = new Chart(monthlyCanvas, {
      type: 'bar',
      data: {
        labels: months,
        datasets: [
          {
            label: 'Total Expenses (₹)',
            data: monthAmounts,
            backgroundColor: '#4f46e5',
            borderRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => ` Total: ${formatINR(ctx.raw)}`,
            },
          },
        },
        scales: {
          x: {
            ticks: { color: textColor },
            grid: { display: false },
          },
          y: {
            ticks: {
              color: textColor,
              callback: (v) => '₹' + v,
            },
            grid: { color: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)' },
          },
        },
      },
    });
  }
}

// --- Summary & Metrics Calculation ---
function updateMetrics() {
  const total = expensesList.reduce((sum, e) => sum + parseFloat(e.amount || 0), 0);
  const count = expensesList.length;
  totalAmountEl.textContent = formatINR(total);
  transactionCountEl.textContent = String(count);

  updateBudgetMonitor();
  renderCharts();
}

// --- Table Rendering with Filtering & Sorting ---
function applyFiltersAndRender() {
  updateMetrics();

  const searchQuery = searchBox.value.toLowerCase().trim();
  const selectedCategory = categoryFilter.value;
  const sortMode = sortBy.value;

  let filtered = expensesList.map((item, index) => ({ ...item, originalIndex: index }));

  // Filter by category
  if (selectedCategory !== 'ALL') {
    filtered = filtered.filter((item) => item.category === selectedCategory);
  }

  // Filter by search query
  if (searchQuery) {
    filtered = filtered.filter(
      (item) =>
        (item.description || '').toLowerCase().includes(searchQuery) ||
        (item.category || '').toLowerCase().includes(searchQuery)
    );
  }

  // Sorting
  filtered.sort((a, b) => {
    if (sortMode === 'date-desc') return new Date(b.date) - new Date(a.date);
    if (sortMode === 'date-asc') return new Date(a.date) - new Date(b.date);
    if (sortMode === 'amount-desc') return parseFloat(b.amount) - parseFloat(a.amount);
    if (sortMode === 'amount-asc') return parseFloat(a.amount) - parseFloat(b.amount);
    return 0;
  });

  tableBody.innerHTML = '';

  if (filtered.length === 0) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="6" class="empty-state">
          <div>🔍</div>
          <p>No matching expenses found.</p>
        </td>
      </tr>
    `;
    tableSummaryText.textContent = `Showing 0 of ${expensesList.length} expenses`;
    return;
  }

  tableSummaryText.textContent = `Showing ${filtered.length} of ${expensesList.length} expenses`;

  filtered.forEach((item, idx) => {
    const row = document.createElement('tr');
    const catClass = `cat-${item.category || 'Other'}`;

    row.innerHTML = `
      <td>${idx + 1}</td>
      <td>${item.date}</td>
      <td><span class="cat-badge ${catClass}">${item.category}</span></td>
      <td><strong>${escapeHtml(item.description)}</strong></td>
      <td class="amount-cell">${formatINR(item.amount)}</td>
      <td style="text-align: center;">
        <button class="delete-row-btn" data-index="${item.originalIndex}" title="Delete expense">
          🗑️ Delete
        </button>
      </td>
    `;
    tableBody.appendChild(row);
  });
}

function escapeHtml(str) {
  return String(str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// --- Action Handlers ---

// 1. Add Expense
form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const category = categoryInput.value.trim();
  const description = descriptionInput.value.trim();
  const amountVal = parseFloat(amountInput.value);
  const date = dateInput.value || getTodayDate();

  if (!category) {
    showToast('Please select a valid category.', 'error');
    return;
  }
  if (!description) {
    showToast('Please enter a description.', 'error');
    return;
  }
  if (isNaN(amountVal) || amountVal <= 0) {
    showToast('Please enter a valid positive amount.', 'error');
    return;
  }

  const newExpense = {
    category,
    description,
    amount: amountVal.toFixed(2),
    date,
  };

  if (isBackendConnected) {
    try {
      const res = await fetch('/api/expenses', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newExpense),
      });
      if (res.ok) {
        showToast('Expense saved to CSV successfully!');
        await loadData();
      } else {
        throw new Error('Failed to save to backend');
      }
    } catch (err) {
      showToast('Error syncing with backend, saved locally.', 'info');
      expensesList.push(newExpense);
      saveLocalExpenses(expensesList);
      applyFiltersAndRender();
    }
  } else {
    expensesList.push(newExpense);
    saveLocalExpenses(expensesList);
    showToast('Expense added locally!');
    applyFiltersAndRender();
  }

  // Reset form
  descriptionInput.value = '';
  amountInput.value = '';
  categoryInput.value = '';
  dateInput.value = getTodayDate();
});

// 2. Delete Expense
tableBody.addEventListener('click', async (e) => {
  const btn = e.target.closest('.delete-row-btn');
  if (!btn) return;

  const originalIndex = parseInt(btn.dataset.index, 10);
  if (isNaN(originalIndex) || originalIndex < 0 || originalIndex >= expensesList.length) return;

  if (isBackendConnected) {
    try {
      const res = await fetch(`/api/expenses/${originalIndex}`, { method: 'DELETE' });
      if (res.ok) {
        showToast('Expense deleted from CSV.');
        await loadData();
        return;
      }
    } catch (err) {
      // fallback
    }
  }

  expensesList.splice(originalIndex, 1);
  saveLocalExpenses(expensesList);
  showToast('Expense removed.');
  applyFiltersAndRender();
});

// 3. Clear All Expenses
clearDataBtn.addEventListener('click', async () => {
  if (expensesList.length === 0) {
    showToast('No expenses to clear.', 'info');
    return;
  }

  const confirmed = confirm('Are you sure you want to delete ALL recorded expenses?');
  if (!confirmed) return;

  if (isBackendConnected) {
    try {
      await fetch('/api/expenses/clear', { method: 'POST' });
    } catch (e) {}
  }

  expensesList = [];
  saveLocalExpenses([]);
  showToast('All expense records cleared.');
  applyFiltersAndRender();
});

// 4. Export CSV
exportCsvBtn.addEventListener('click', () => {
  if (isBackendConnected) {
    window.location.href = '/api/export';
    showToast('Downloading CSV from server...');
    return;
  }

  // Client-side CSV generation
  if (expensesList.length === 0) {
    showToast('No expenses available to export.', 'info');
    return;
  }

  let csvContent = 'Date,Category,Description,Amount\n';
  expensesList.forEach((e) => {
    const desc = `"${(e.description || '').replace(/"/g, '""')}"`;
    csvContent += `${e.date},${e.category},${desc},${parseFloat(e.amount || 0).toFixed(2)}\n`;
  });

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `expenses_${getTodayDate()}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast('CSV downloaded successfully!');
});

// 5. Search & Filter Listeners
searchBox.addEventListener('input', applyFiltersAndRender);
categoryFilter.addEventListener('change', applyFiltersAndRender);
sortBy.addEventListener('change', applyFiltersAndRender);
monthlyBudgetInput.addEventListener('input', updateBudgetMonitor);

// 6. Chart Tabs
doughnutTabBtn.addEventListener('click', () => {
  doughnutTabBtn.classList.add('active');
  barTabBtn.classList.remove('active');
  categoryCanvas.style.display = 'block';
  monthlyCanvas.style.display = 'none';
});

barTabBtn.addEventListener('click', () => {
  barTabBtn.classList.add('active');
  doughnutTabBtn.classList.remove('active');
  categoryCanvas.style.display = 'none';
  monthlyCanvas.style.display = 'block';
});

// --- Initialize App ---
(async function init() {
  // Budget restore
  const savedBudget = localStorage.getItem(BUDGET_KEY);
  if (savedBudget) {
    monthlyBudgetInput.value = savedBudget;
  }

  // Set default date
  dateInput.value = getTodayDate();

  // Connect to backend / load data
  await checkBackendConnection();
  await loadData();
})();
