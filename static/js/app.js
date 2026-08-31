const state = {
  selectedFile: null,
  outputFormat: '',
  isConverting: false,
  supportedFormats: {},
  conversionHistory: [],
  isDarkMode: true,
  ffmpegAvailable: false
};

// Elements
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const fileInfoArea = document.getElementById('file-info-area');
const fileName = document.getElementById('file-name');
const fileSize = document.getElementById('file-size');
const fileIcon = document.getElementById('file-icon');
const inputFormatBadge = document.getElementById('input-format-badge');
const outputFormatSelect = document.getElementById('output-format-select');
const convertBtn = document.getElementById('convert-btn');
const progressArea = document.getElementById('progress-area');
const progressBar = document.getElementById('progress-bar');
const progressPercentage = document.getElementById('progress-percentage');
const resultArea = document.getElementById('result-area');
const resultFilename = document.getElementById('result-filename');
const downloadBtn = document.getElementById('download-btn');
const convertAnotherBtn = document.getElementById('convert-another-btn');
const themeToggle = document.getElementById('theme-toggle');
const historyList = document.getElementById('history-list');
const formatCardsGrid = document.getElementById('format-cards-grid');
const toastContainer = document.getElementById('toast-container');

// Icons
const icons = {
  image: '🖼️',
  document: '📄',
  spreadsheet: '📊',
  audio: '🎵',
  video: '🎬',
  archive: '📦',
  data: '💾',
  default: '📁'
};

const sunIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>`;
const moonIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>`;

document.addEventListener('DOMContentLoaded', init);

async function init() {
  setupTheme();
  setupEventListeners();
  loadHistory();
  await fetchFormats();
  await checkHealth();
}

function setupTheme() {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    state.isDarkMode = savedTheme === 'dark';
  } else {
    state.isDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  }
  applyTheme();
}

function applyTheme() {
  if (state.isDarkMode) {
    document.body.classList.add('dark-mode');
    document.body.classList.remove('light-mode');
    themeToggle.innerHTML = sunIcon;
  } else {
    document.body.classList.add('light-mode');
    document.body.classList.remove('dark-mode');
    themeToggle.innerHTML = moonIcon;
  }
}

function toggleTheme() {
  state.isDarkMode = !state.isDarkMode;
  localStorage.setItem('theme', state.isDarkMode ? 'dark' : 'light');
  applyTheme();
}

function setupEventListeners() {
  themeToggle.addEventListener('click', toggleTheme);

  // Drop zone events
  dropZone.addEventListener('dragenter', (e) => { e.preventDefault(); dropZone.classList.add('active'); });
  dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('active'); });
  dropZone.addEventListener('dragleave', (e) => { e.preventDefault(); dropZone.classList.remove('active'); });
  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('active');
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  });
  dropZone.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelect(e.target.files[0]);
    }
  });

  // Conversion events
  outputFormatSelect.addEventListener('change', (e) => {
    state.outputFormat = e.target.value;
    convertBtn.disabled = !state.selectedFile || !state.outputFormat;
  });

  convertBtn.addEventListener('click', convertFile);
  convertAnotherBtn.addEventListener('click', resetConverter);
}

async function fetchFormats() {
  try {
    // In a real app, this would be: const response = await fetch('/api/formats');
    // For this demonstration, we'll mock the response based on the prompt if the endpoint fails
    let data;
    try {
      const response = await fetch('/api/formats');
      if (response.ok) {
        data = await response.json();
      } else {
        throw new Error('API failed');
      }
    } catch (e) {
      // Mock data based on requirements
      data = {
        image: { extensions: ['png', 'jpg', 'jpeg', 'bmp', 'gif', 'webp', 'tiff', 'ico'], outputs: ['png', 'jpg', 'webp', 'gif'] },
        document: { extensions: ['docx', 'txt', 'md', 'html', 'pdf'], outputs: ['pdf', 'docx', 'txt'] },
        spreadsheet: { extensions: ['xlsx', 'csv', 'json', 'tsv'], outputs: ['csv', 'xlsx', 'json'] },
        audio: { extensions: ['mp3', 'wav', 'ogg', 'flac', 'aac', 'm4a'], outputs: ['mp3', 'wav', 'ogg'] },
        video: { extensions: ['mp4', 'avi', 'mkv', 'mov', 'webm', 'flv'], outputs: ['mp4', 'webm', 'avi'] },
        archive: { extensions: ['zip', 'tar', 'gz', 'tgz', '7z'], outputs: ['zip', 'tar.gz'] },
        data: { extensions: ['json', 'yaml', 'yml', 'xml', 'csv', 'tsv'], outputs: ['json', 'xml', 'yaml'] }
      };
    }
    
    state.supportedFormats = data;
    renderFormatCards();
  } catch (error) {
    showToast('Failed to load supported formats', 'error');
  }
}

async function checkHealth() {
  try {
    const response = await fetch('/api/health');
    if (response.ok) {
      const data = await response.json();
      state.ffmpegAvailable = data.ffmpeg_available;
    }
  } catch (e) {
    // silently fail
  }
}

function handleFileSelect(file) {
  // Max size 100MB
  if (file.size > 100 * 1024 * 1024) {
    showToast('File size exceeds 100MB limit', 'error');
    return;
  }

  state.selectedFile = file;
  state.outputFormat = '';
  
  const ext = getFileExtension(file.name);
  const category = getFormatCategory(ext);
  
  showFileInfo(file, ext, category);
  populateOutputFormats(ext, category);
  
  dropZone.classList.add('hidden');
  fileInfoArea.classList.remove('hidden');
  convertBtn.disabled = true;
}

function showFileInfo(file, ext, category) {
  fileName.textContent = file.name;
  fileName.title = file.name;
  fileSize.textContent = formatFileSize(file.size);
  fileIcon.textContent = getFileIcon(category);
  inputFormatBadge.textContent = ext || 'unknown';
  inputFormatBadge.className = `format-badge badge-${category || 'data'}`;
}

function populateOutputFormats(inputExt, category) {
  outputFormatSelect.innerHTML = '<option value="" disabled selected>Select output</option>';
  
  if (!category || !state.supportedFormats[category]) {
    // If unknown category, show all categories
    for (const cat in state.supportedFormats) {
      const optgroup = document.createElement('optgroup');
      optgroup.label = cat.charAt(0).toUpperCase() + cat.slice(1);
      
      const outputs = state.supportedFormats[cat].outputs || state.supportedFormats[cat].extensions;
      outputs.forEach(format => {
        if (format !== inputExt) {
          const option = document.createElement('option');
          option.value = format;
          option.textContent = format.toUpperCase();
          optgroup.appendChild(option);
        }
      });
      outputFormatSelect.appendChild(optgroup);
    }
    return;
  }

  // Show outputs for the detected category
  const outputs = state.supportedFormats[category].outputs || state.supportedFormats[category].extensions;
  outputs.forEach(format => {
    if (format !== inputExt) {
      const option = document.createElement('option');
      option.value = format;
      option.textContent = format.toUpperCase();
      outputFormatSelect.appendChild(option);
    }
  });
}

function convertFile() {
  if (!state.selectedFile || !state.outputFormat) return;

  state.isConverting = true;
  convertBtn.disabled = true;
  outputFormatSelect.disabled = true;
  
  progressArea.classList.remove('hidden');
  showProgress(0);

  const formData = new FormData();
  formData.append('file', state.selectedFile);
  formData.append('output_format', state.outputFormat);

  const xhr = new XMLHttpRequest();
  xhr.open('POST', '/api/convert', true);

  xhr.upload.onprogress = (e) => {
    if (e.lengthComputable) {
      // Upload is first 50% of progress
      const percentComplete = (e.loaded / e.total) * 50;
      showProgress(percentComplete);
    }
  };

  xhr.onload = function() {
    if (xhr.status >= 200 && xhr.status < 300) {
      showProgress(100);
      try {
        const response = JSON.parse(xhr.responseText);
        if (response.success || response.filename) {
          setTimeout(() => showResult(response), 500);
        } else {
          handleConversionError(response.error || response.detail || 'Conversion failed');
        }
      } catch (e) {
        handleConversionError('Invalid response from server');
      }
    } else {
      try {
        const errData = JSON.parse(xhr.responseText);
        handleConversionError(errData.detail || `Error: ${xhr.statusText}`);
      } catch (e) {
        handleConversionError(`Error ${xhr.status}: ${xhr.statusText}`);
      }
    }
  };

  xhr.onerror = function() {
    handleConversionError('Network error. Please make sure the server is running.');
  };

  xhr.send(formData);
}

function handleConversionError(msg) {
  showToast(msg, 'error');
  resetConverter();
}

function showProgress(percent) {
  const rounded = Math.round(percent);
  progressBar.style.width = `${rounded}%`;
  progressPercentage.textContent = `${rounded}%`;
  const progressText = document.querySelector('.progress-text');
  if (rounded < 50) {
    progressText.textContent = 'Uploading...';
  } else if (rounded < 100) {
    progressText.textContent = 'Converting...';
  } else {
    progressText.textContent = 'Finishing up...';
  }
}

function showResult(data) {
  progressArea.classList.add('hidden');
  resultArea.classList.remove('hidden');
  resultFilename.textContent = data.filename;
  
  // Create history item
  const historyItem = {
    id: Date.now(),
    filename: data.original_name,
    inputFormat: data.original_format,
    outputFormat: data.output_format,
    downloadUrl: data.download_url || `/api/download/${data.filename}`,
    timestamp: new Date().toISOString()
  };
  
  addToHistory(historyItem);

  // Setup download button
  downloadBtn.onclick = () => {
    if (data.download_url === '#') {
      showToast('Demo mode: Download simulated successfully', 'success');
    } else {
      downloadFile(historyItem.downloadUrl, data.filename);
    }
  };
  
  showToast('Conversion successful!', 'success');
}

function downloadFile(url, filename) {
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

function resetConverter() {
  state.selectedFile = null;
  state.outputFormat = '';
  state.isConverting = false;
  
  fileInput.value = '';
  outputFormatSelect.value = '';
  outputFormatSelect.disabled = false;
  
  resultArea.classList.add('hidden');
  fileInfoArea.classList.add('hidden');
  progressArea.classList.add('hidden');
  dropZone.classList.remove('hidden');
}

function renderFormatCards() {
  formatCardsGrid.innerHTML = '';
  
  for (const [category, data] of Object.entries(state.supportedFormats)) {
    const card = document.createElement('div');
    card.className = 'format-card';
    
    const header = document.createElement('div');
    header.className = 'format-card-header';
    
    const icon = document.createElement('span');
    icon.className = 'format-card-icon';
    icon.textContent = getFileIcon(category);
    
    const title = document.createElement('h3');
    title.className = 'format-card-title';
    title.textContent = category.charAt(0).toUpperCase() + category.slice(1);
    
    header.appendChild(icon);
    header.appendChild(title);
    
    const badgeList = document.createElement('div');
    badgeList.className = 'format-badge-list';
    
    const extensions = data.extensions || [];
    // Show up to 10 extensions to keep it clean
    const displayExts = extensions.slice(0, 10);
    
    displayExts.forEach(ext => {
      const badge = document.createElement('span');
      badge.className = `format-card-badge badge-${category}`;
      badge.textContent = ext;
      badgeList.appendChild(badge);
    });
    
    if (extensions.length > 10) {
      const more = document.createElement('span');
      more.className = `format-card-badge badge-${category}`;
      more.textContent = `+${extensions.length - 10} more`;
      badgeList.appendChild(more);
    }
    
    card.appendChild(header);
    card.appendChild(badgeList);
    formatCardsGrid.appendChild(card);
  }
}

// History Management
function loadHistory() {
  const saved = sessionStorage.getItem('conversionHistory');
  if (saved) {
    try {
      state.conversionHistory = JSON.parse(saved);
      renderHistory();
    } catch (e) {
      console.error('Failed to parse history');
    }
  }
}

function addToHistory(item) {
  state.conversionHistory.unshift(item);
  if (state.conversionHistory.length > 10) {
    state.conversionHistory.pop();
  }
  sessionStorage.setItem('conversionHistory', JSON.stringify(state.conversionHistory));
  renderHistory();
}

function renderHistory() {
  if (state.conversionHistory.length === 0) {
    historyList.innerHTML = '<p class="empty-history">No recent conversions in this session.</p>';
    return;
  }
  
  historyList.innerHTML = '';
  
  state.conversionHistory.forEach(item => {
    const el = document.createElement('div');
    el.className = 'history-item';
    
    const time = new Date(item.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    
    el.innerHTML = `
      <div class="history-item-info">
        <span class="history-filename">${item.filename}</span>
        <span class="history-meta">${item.inputFormat.toUpperCase()} to ${item.outputFormat.toUpperCase()} • ${time}</span>
      </div>
      <button class="btn btn-outline" style="padding: 6px 12px; font-size: 12px;">Download</button>
    `;
    
    const btn = el.querySelector('button');
    btn.onclick = () => {
      if (item.downloadUrl === '#') {
        showToast('Demo mode: Download simulated successfully', 'success');
      } else {
        downloadFile(item.downloadUrl, `converted_${item.filename.split('.')[0]}.${item.outputFormat}`);
      }
    };
    
    historyList.appendChild(el);
  });
}

// Utilities
function getFileExtension(filename) {
  return filename.slice((filename.lastIndexOf(".") - 1 >>> 0) + 2).toLowerCase();
}

function getFormatCategory(extension) {
  for (const [category, data] of Object.entries(state.supportedFormats)) {
    if (data.extensions && data.extensions.includes(extension)) {
      return category;
    }
  }
  return 'default';
}

function getFileIcon(category) {
  return icons[category] || icons.default;
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  
  toastContainer.appendChild(toast);
  
  setTimeout(() => {
    toast.classList.add('toast-fade-out');
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 300);
  }, 5000);
}
