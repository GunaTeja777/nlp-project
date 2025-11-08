// DOM Elements
const questionInput = document.getElementById('questionInput');
const submitBtn = document.getElementById('submitBtn');
const errorMessage = document.getElementById('errorMessage');
const loadingSpinner = document.getElementById('loadingSpinner');
const resultsSection = document.getElementById('resultsSection');

// Stats elements
const difficultyLevel = document.getElementById('difficultyLevel');
const paragraphCount = document.getElementById('paragraphCount');
const keywordCount = document.getElementById('keywordCount');

// Content elements
const summaryContent = document.getElementById('summaryContent');
const keywordsContainer = document.getElementById('keywordsContainer');
const keywordCountDisplay = document.getElementById('keywordCountDisplay');
const keyPointsContainer = document.getElementById('keyPointsContainer');
const keyPointsCountDisplay = document.getElementById('keyPointsCountDisplay');
const paragraphsContainer = document.getElementById('paragraphsContainer');
const fullAnswerContent = document.getElementById('fullAnswerContent');

// State
let isProcessing = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAPIHealth();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    submitBtn.addEventListener('click', handleSubmit);
    
    questionInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !isProcessing) {
            handleSubmit();
        }
    });

    questionInput.addEventListener('input', () => {
        hideError();
    });
}

// Check API Health
async function checkAPIHealth() {
    try {
        const response = await apiService.healthCheck();
        if (response.status !== 'healthy') {
            console.warn('API is not healthy:', response.message);
        }
    } catch (error) {
        console.error('Failed to connect to backend:', error);
        showError('Backend server is not running. Please start the Flask server.');
    }
}

// Handle Submit
async function handleSubmit() {
    const question = questionInput.value.trim();

    if (!question) {
        showError('Please enter a question');
        questionInput.focus();
        return;
    }

    if (isProcessing) {
        return;
    }

    try {
        isProcessing = true;
        hideError();
        hideResults();
        showLoading();
        disableInput();

        const response = await apiService.getAnswer(question);

        if (response.success) {
            displayResults(response.result);
        } else {
            throw new Error(response.error || 'Failed to get answer');
        }

    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'An error occurred. Please try again.');
        hideLoading();
    } finally {
        isProcessing = false;
        enableInput();
    }
}

// Display Results
function displayResults(result) {
    hideLoading();

    console.log('Received result:', result); // Debug log

    // Update stats
    updateStats(result);

    // Update summary
    summaryContent.textContent = result.summary;

    // Update keywords
    displayKeywords(result.keywords);

    // Update key points
    displayKeyPoints(result.key_points);

    // Update paragraphs
    displayParagraphs(result.paragraphs);

    // Update full answer
    fullAnswerContent.textContent = result.full_answer;

    // Show results
    showResults();
}

// Update Statistics
function updateStats(result) {
    // Difficulty level
    difficultyLevel.textContent = result.difficulty;
    difficultyLevel.className = 'stat-value ' + result.difficulty.toLowerCase();

    // Paragraph count
    paragraphCount.textContent = result.paragraphs.length;

    // Keyword count
    keywordCount.textContent = result.keywords.length;
}

// Display Keywords
function displayKeywords(keywords) {
    console.log('Displaying keywords:', keywords); // Debug log
    keywordsContainer.innerHTML = '';
    
    if (!keywords || keywords.length === 0) {
        keywordsContainer.innerHTML = '<p style="color: #666; padding: 10px;">No keywords extracted.</p>';
        keywordCountDisplay.textContent = '0';
        return;
    }
    
    keywordCountDisplay.textContent = keywords.length;
    
    keywords.forEach((keyword, index) => {
        const tag = document.createElement('span');
        tag.className = 'keyword-tag';
        tag.textContent = keyword;
        tag.style.animationDelay = `${index * 0.1}s`;
        keywordsContainer.appendChild(tag);
    });
}

// Display Key Points
function displayKeyPoints(keyPoints) {
    keyPointsContainer.innerHTML = '';
    keyPointsCountDisplay.textContent = keyPoints.length;
    
    if (!keyPoints || keyPoints.length === 0) {
        keyPointsContainer.innerHTML = '<p style="color: #666;">No key points extracted.</p>';
        return;
    }
    
    const list = document.createElement('ul');
    list.className = 'key-points-list';
    
    keyPoints.forEach((point, index) => {
        const item = document.createElement('li');
        item.className = 'key-point-item';
        item.style.animationDelay = `${index * 0.1}s`;
        item.innerHTML = `<i class="fas fa-check-circle"></i><span>${point}</span>`;
        list.appendChild(item);
    });
    
    keyPointsContainer.appendChild(list);
}

// Display Paragraphs
function displayParagraphs(paragraphs) {
    paragraphsContainer.innerHTML = '';
    
    paragraphs.forEach((paragraph, index) => {
        const block = document.createElement('div');
        block.className = 'paragraph-block';
        block.style.animationDelay = `${index * 0.15}s`;
        
        const title = document.createElement('div');
        title.className = 'paragraph-title';
        title.innerHTML = `<i class="fas fa-paragraph"></i> Paragraph ${index + 1}`;
        
        const text = document.createElement('p');
        text.className = 'paragraph-text';
        text.textContent = paragraph;
        
        block.appendChild(title);
        block.appendChild(text);
        paragraphsContainer.appendChild(block);
    });
}

// UI Helper Functions
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.add('show');
}

function hideError() {
    errorMessage.classList.remove('show');
}

function showLoading() {
    loadingSpinner.classList.add('show');
}

function hideLoading() {
    loadingSpinner.classList.remove('show');
}

function showResults() {
    resultsSection.style.display = 'block';
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

function hideResults() {
    resultsSection.style.display = 'none';
}

function disableInput() {
    questionInput.disabled = true;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Processing...</span>';
}

function enableInput() {
    questionInput.disabled = false;
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<i class="fas fa-search"></i><span>Get Answer</span>';
}