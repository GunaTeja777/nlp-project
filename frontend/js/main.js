// DOM Elements
const questionInput = document.getElementById('questionInput');
const submitBtn = document.getElementById('submitBtn');
const errorMessage = document.getElementById('errorMessage');
const welcomeState = document.getElementById('welcomeState');
const loadingSpinner = document.getElementById('loadingSpinner');
const resultsSection = document.getElementById('resultsSection');

// Result elements
const difficultyBadge = document.getElementById('difficultyBadge');
const statDifficulty = document.getElementById('statDifficulty');
const statKeywords = document.getElementById('statKeywords');
const statWords = document.getElementById('statWords');
const summaryContent = document.getElementById('summaryContent');
const fullAnswerContent = document.getElementById('fullAnswerContent');
const keywordsContainer = document.getElementById('keywordsContainer');
const keyPointsContainer = document.getElementById('keyPointsContainer');
const paragraphsContainer = document.getElementById('paragraphsContainer');

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
        hideWelcome();
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

    // Update stats row
    updateStatsRow(result);

    // Update difficulty badge
    updateDifficultyBadge(result.difficulty);

    // Update summary
    summaryContent.textContent = result.summary;

    // Update full answer
    fullAnswerContent.textContent = result.full_answer;

    // Update keywords
    displayKeywords(result.keywords || []);

    // Update key points
    displayKeyPoints(result.key_points || []);

    // Update paragraphs
    displayParagraphs(result.paragraphs || []);

    // Show results
    showResults();
}

// Update Stats Row
function updateStatsRow(result) {
    // Difficulty Level
    if (statDifficulty) {
        const difficulty = result.difficulty || 'Intermediate';
        statDifficulty.textContent = difficulty;
        statDifficulty.className = 'stat-value difficulty-' + difficulty.toLowerCase();
    }

    // Keywords Count
    if (statKeywords) {
        const keywordCount = (result.keywords && result.keywords.length) || 0;
        statKeywords.textContent = keywordCount;
    }

    // Word Count
    if (statWords) {
        const fullAnswer = result.full_answer || '';
        const wordCount = fullAnswer.trim().split(/\s+/).filter(word => word.length > 0).length;
        statWords.textContent = wordCount;
    }
}

// Update Difficulty Badge
function updateDifficultyBadge(difficulty) {
    if (!difficultyBadge) return;
    
    difficultyBadge.textContent = difficulty || 'Intermediate';
    difficultyBadge.className = 'difficulty-badge';
    
    if (difficulty) {
        difficultyBadge.classList.add(difficulty.toLowerCase());
    }
}

// Display Keywords
function displayKeywords(keywords) {
    console.log('Displaying keywords:', keywords); // Debug log
    keywordsContainer.innerHTML = '';
    
    if (!keywords || keywords.length === 0) {
        keywordsContainer.innerHTML = '<p style="color: var(--text-secondary);">No keywords extracted.</p>';
        return;
    }
    
    keywords.forEach((keyword, index) => {
        const tag = document.createElement('span');
        tag.className = 'keyword-tag';
        tag.textContent = keyword;
        tag.style.animationDelay = `${index * 0.05}s`;
        keywordsContainer.appendChild(tag);
    });
}

// Display Key Points
function displayKeyPoints(keyPoints) {
    keyPointsContainer.innerHTML = '';
    
    if (!keyPoints || keyPoints.length === 0) {
        keyPointsContainer.innerHTML = '<p style="color: var(--text-secondary);">No key points extracted.</p>';
        return;
    }
    
    keyPoints.forEach((point, index) => {
        const item = document.createElement('div');
        item.className = 'key-point-item';
        item.style.animationDelay = `${index * 0.05}s`;
        item.innerHTML = `<i class="fas fa-check-circle"></i><span>${point}</span>`;
        keyPointsContainer.appendChild(item);
    });
}

// Display Paragraphs
function displayParagraphs(paragraphs) {
    paragraphsContainer.innerHTML = '';
    
    if (!paragraphs || paragraphs.length === 0) {
        paragraphsContainer.innerHTML = '<p style="color: var(--text-secondary);">No paragraphs available.</p>';
        return;
    }
    
    paragraphs.forEach((paragraph, index) => {
        const block = document.createElement('div');
        block.className = 'paragraph-block';
        block.style.animationDelay = `${index * 0.05}s`;
        
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

function showWelcome() {
    if (welcomeState) {
        welcomeState.style.display = 'flex';
    }
}

function hideWelcome() {
    if (welcomeState) {
        welcomeState.style.display = 'none';
    }
}

function showLoading() {
    loadingSpinner.style.display = 'flex';
}

function hideLoading() {
    loadingSpinner.style.display = 'none';
}

function showResults() {
    resultsSection.style.display = 'block';
    resultsSection.classList.add('show');
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

function hideResults() {
    resultsSection.style.display = 'none';
    resultsSection.classList.remove('show');
}

function disableInput() {
    questionInput.disabled = true;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span>Processing...</span>';
}

function enableInput() {
    questionInput.disabled = false;
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<span>Analyze Answer</span>';
}