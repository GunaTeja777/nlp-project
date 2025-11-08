from collections import Counter
import re

class NLPProcessor:
    """Handles all NLP processing tasks - Simplified version"""
    
    def __init__(self):
        # Common English stop words (expanded list)
        self.stop_words = {
            'the', 'is', 'at', 'which', 'on', 'a', 'an', 'as', 'are', 
            'was', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 
            'does', 'did', 'will', 'would', 'should', 'could', 'may', 
            'might', 'must', 'can', 'of', 'for', 'to', 'in', 'and', 
            'or', 'but', 'not', 'with', 'by', 'from', 'this', 'that',
            'these', 'those', 'it', 'its', 'they', 'them', 'their',
            'about', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'between', 'under', 'again', 'further',
            'then', 'once', 'here', 'there', 'when', 'where', 'why',
            'how', 'all', 'both', 'each', 'few', 'more', 'most', 'other',
            'some', 'such', 'only', 'own', 'same', 'so', 'than', 'too',
            'very', 'just', 'also', 'being', 'having', 'doing'
        }
        
        # Common noun/adjective indicators (simplified POS)
        self.noun_indicators = {'tion', 'sion', 'ment', 'ness', 'ity', 'ism', 'ology', 'ance', 'ence'}
        self.adj_indicators = {'ful', 'less', 'ous', 'ive', 'able', 'ible', 'al', 'ic', 'ical'}
    
    def _is_likely_noun_or_adj(self, word):
        """Simple POS detection based on word endings (linguistic features)"""
        word_lower = word.lower()
        # Check noun suffixes
        if any(word_lower.endswith(suffix) for suffix in self.noun_indicators):
            return True
        # Check adjective suffixes
        if any(word_lower.endswith(suffix) for suffix in self.adj_indicators):
            return True
        # Capitalized words (proper nouns) - but not at start
        if word[0].isupper() and len(word) > 3:
            return True
        return False
    
    def _calculate_word_score(self, word, word_freq, total_words, position_factor):
        """Calculate importance score combining multiple factors (TF-IDF inspired)"""
        word_lower = word.lower()
        
        # Base frequency score (TF - Term Frequency)
        tf_score = word_freq[word_lower] / total_words
        
        # IDF approximation - longer, rarer words get higher scores
        # (In real IDF, we'd compare across documents, here we use word characteristics)
        length_score = min(len(word) / 15, 1.5)  # Longer words often more important
        
        # Position bonus - words appearing early are often more important
        position_score = 1.0 + (position_factor * 0.3)
        
        # Linguistic feature bonus (noun/adjective detection)
        pos_bonus = 1.5 if self._is_likely_noun_or_adj(word) else 1.0
        
        # Capitalization bonus (proper nouns, technical terms)
        cap_bonus = 1.3 if word[0].isupper() and len(word) > 3 else 1.0
        
        # Combined score
        final_score = tf_score * length_score * position_score * pos_bonus * cap_bonus
        
        return final_score
    
    def _extract_phrases(self, text):
        """RAKE-inspired phrase extraction - find multi-word keywords"""
        # Split by stopwords to get candidate phrases
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        phrases = []
        current_phrase = []
        
        for word in words:
            if word.lower() in self.stop_words or len(word) < 3:
                if current_phrase and len(current_phrase) >= 2:
                    phrases.append(' '.join(current_phrase))
                current_phrase = []
            else:
                current_phrase.append(word)
        
        # Add last phrase if exists
        if current_phrase and len(current_phrase) >= 2:
            phrases.append(' '.join(current_phrase))
        
        return phrases
    
    def extract_keywords(self, text, min_keywords=5, max_keywords=12):
        """Advanced keyword extraction using TF-IDF, POS, and RAKE techniques"""
        if not text or len(text.strip()) < 10:
            return []
        
        # Step 1: Preprocessing - Extract words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text)  # Min 3 characters
        
        if not words:
            return []
        
        # Step 2: Filter stopwords and calculate frequency (TF)
        filtered_words = [w for w in words if w.lower() not in self.stop_words]
        
        if not filtered_words:
            return []
        
        word_freq = Counter(w.lower() for w in filtered_words)
        total_words = len(filtered_words)
        
        # Step 3: Calculate importance scores for single words
        word_scores = {}
        word_positions = {}  # Track first occurrence
        
        for idx, word in enumerate(filtered_words):
            word_lower = word.lower()
            if word_lower not in word_positions:
                word_positions[word_lower] = idx
        
        for word_lower in word_freq.keys():
            if len(word_lower) >= 4:  # Focus on meaningful words
                position_factor = 1.0 - (word_positions[word_lower] / len(filtered_words))
                # Use original capitalization from first occurrence
                original_word = next(w for w in filtered_words if w.lower() == word_lower)
                score = self._calculate_word_score(
                    original_word, 
                    word_freq, 
                    total_words, 
                    position_factor
                )
                word_scores[word_lower] = score
        
        # Step 4: RAKE - Extract multi-word phrases
        phrases = self._extract_phrases(text)
        phrase_scores = {}
        
        for phrase in phrases:
            if len(phrase) > 20:  # Skip very long phrases
                continue
            phrase_words = phrase.lower().split()
            # Score phrase by sum of word scores
            score = sum(word_scores.get(w, 0) for w in phrase_words)
            # Bonus for phrase length
            score *= (1 + len(phrase_words) * 0.2)
            phrase_scores[phrase.lower()] = score
        
        # Step 5: Combine single words and phrases
        all_keywords = {}
        all_keywords.update(word_scores)
        all_keywords.update(phrase_scores)
        
        # Step 6: Rank and select keywords dynamically
        sorted_keywords = sorted(all_keywords.items(), key=lambda x: x[1], reverse=True)
        
        # Calculate threshold for meaningful keywords
        if sorted_keywords:
            max_score = sorted_keywords[0][1]
            # Only include keywords with score > 20% of top keyword
            threshold = max_score * 0.2
        else:
            return []
        
        # Return unique keywords above threshold (between min and max)
        final_keywords = []
        seen = set()
        
        for keyword, score in sorted_keywords:
            # Skip if below threshold
            if score < threshold:
                break
            
            # Avoid duplicates and substrings
            if keyword not in seen and not any(keyword in k or k in keyword for k in seen):
                final_keywords.append(keyword)
                seen.add(keyword)
            
            # Limit to max_keywords
            if len(final_keywords) >= max_keywords:
                break
        
        # Ensure we return at least min_keywords if available
        if len(final_keywords) < min_keywords and len(sorted_keywords) >= min_keywords:
            for keyword, score in sorted_keywords:
                if keyword not in seen and not any(keyword in k or k in keyword for k in seen):
                    final_keywords.append(keyword)
                    seen.add(keyword)
                if len(final_keywords) >= min_keywords:
                    break
        
        return final_keywords
    
    def create_paragraphs(self, text):
        """Divide text into structured paragraphs"""
        # First check if text already has paragraph breaks
        if '\n\n' in text:
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            if paragraphs:
                return paragraphs
        
        # Check for single newlines
        if '\n' in text:
            paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
            if len(paragraphs) > 1:
                return paragraphs
        
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        sentences = [s for s in sentences if s.strip()]
        
        if len(sentences) <= 3:
            return [text]  # Return as single paragraph if short
        
        paragraphs = []
        current_paragraph = []
        
        # Group sentences into paragraphs (2-4 sentences each)
        for i, sentence in enumerate(sentences):
            current_paragraph.append(sentence)
            
            # Create paragraph every 3 sentences or at the end
            if len(current_paragraph) >= 3 or i == len(sentences) - 1:
                if current_paragraph:  # Only add if not empty
                    paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = []
        
        return paragraphs if paragraphs else [text]
    
    def predict_difficulty(self, text):
        """Predict difficulty level of the text"""
        # Simple word and sentence extraction
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s for s in sentences if s.strip()]
        
        if not words or not sentences:
            return "Beginner"
        
        # Calculate average word length
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Calculate average sentence length
        avg_sentence_length = len(words) / len(sentences)
        
        # Count complex words (more than 7 characters or 3+ syllables)
        complex_words = sum(1 for word in words if len(word) > 7 or self._count_syllables(word) > 3)
        complex_ratio = complex_words / len(words) if words else 0
        
        # Count technical/academic words (words > 10 characters)
        technical_words = sum(1 for word in words if len(word) > 10)
        technical_ratio = technical_words / len(words) if words else 0
        
        # Calculate difficulty score (0-10)
        score = 0
        
        # Word length scoring (0-3 points)
        if avg_word_length > 6.5:
            score += 3
        elif avg_word_length > 5.5:
            score += 2
        elif avg_word_length > 4.5:
            score += 1
        
        # Sentence length scoring (0-3 points)
        if avg_sentence_length > 25:
            score += 3
        elif avg_sentence_length > 18:
            score += 2
        elif avg_sentence_length > 12:
            score += 1
        
        # Complex words scoring (0-2 points)
        if complex_ratio > 0.20:
            score += 2
        elif complex_ratio > 0.12:
            score += 1
        
        # Technical words scoring (0-2 points)
        if technical_ratio > 0.08:
            score += 2
        elif technical_ratio > 0.04:
            score += 1
        
        # Determine difficulty based on score
        if score >= 7:
            return "Advanced"
        elif score >= 4:
            return "Intermediate"
        else:
            return "Beginner"
    
    def _count_syllables(self, word):
        """Estimate syllable count in a word"""
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        if word.endswith('e'):
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def generate_summary(self, text, max_length=150):
        """Generate a concise summary"""
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        sentences = [s for s in sentences if s.strip()]
        
        if len(sentences) <= 2:
            return text
        
        # Extractive summarization: Take first, last, and one middle sentence
        if len(sentences) > 3:
            # Score sentences by keyword density
            sentence_scores = {}
            for sent in sentences[1:-1]:  # Skip first and last
                words = re.findall(r'\b[a-zA-Z]{4,}\b', sent.lower())
                words = [w for w in words if w not in self.stop_words]
                sentence_scores[sent] = len(words)
            
            if sentence_scores:
                important_sentence = max(sentence_scores.items(), key=lambda x: x[1])[0]
                summary = f"{sentences[0]} {important_sentence} {sentences[-1]}"
            else:
                summary = f"{sentences[0]} {sentences[-1]}"
        else:
            summary = ' '.join(sentences[:2])
        
        return summary
    
    def analyze_question_difficulty(self, question):
        """Analyze the difficulty of a question based on multiple factors"""
        question = question.strip()
        
        if not question:
            return "Beginner"
        
        # Extract words and calculate metrics
        words = re.findall(r'\b[a-zA-Z]+\b', question)
        word_count = len(words)
        
        if word_count == 0:
            return "Beginner"
        
        # 1. Word Complexity Analysis
        avg_word_length = sum(len(w) for w in words) / word_count
        complex_words = sum(1 for w in words if len(w) > 8 or self._count_syllables(w) > 3)
        complex_ratio = complex_words / word_count
        
        # 2. Sentence Length
        sentences = re.split(r'[.!?]+', question)
        sentences = [s for s in sentences if s.strip()]
        avg_sentence_length = word_count / max(len(sentences), 1)
        
        # 3. Calculate Flesch Reading Ease Score (simplified)
        # Formula: 206.835 - 1.015(words/sentences) - 84.6(syllables/words)
        total_syllables = sum(self._count_syllables(w) for w in words)
        syllables_per_word = total_syllables / word_count
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * syllables_per_word)
        flesch_score = max(0, min(100, flesch_score))  # Clamp between 0-100
        
        # 4. Identify concepts (count nouns and technical terms)
        technical_terms = sum(1 for w in words if len(w) > 10)
        potential_concepts = sum(1 for w in words if len(w) > 5 and w.lower() not in self.stop_words)
        
        # 5. Question Type Classification
        question_lower = question.lower()
        
        # Bloom's Taxonomy Keywords
        easy_verbs = ['what', 'who', 'when', 'where', 'list', 'define', 'name', 'identify', 'recall']
        medium_verbs = ['how', 'why', 'explain', 'describe', 'compare', 'contrast', 'classify', 'demonstrate']
        hard_verbs = ['analyze', 'evaluate', 'design', 'create', 'synthesize', 'justify', 'critique', 'assess', 'develop']
        
        question_type_score = 0
        if any(verb in question_lower for verb in easy_verbs):
            question_type_score = 1
        elif any(verb in question_lower for verb in medium_verbs):
            question_type_score = 2
        elif any(verb in question_lower for verb in hard_verbs):
            question_type_score = 3
        else:
            question_type_score = 2  # Default to medium
        
        # 6. Negation Detection
        has_negation = any(neg in question_lower for neg in ['not', "n't", 'never', 'neither', 'nor', 'except'])
        
        # 7. Multiple topics detection (using 'and', 'or', multiple question marks)
        has_multiple_topics = question_lower.count(' and ') > 0 or question_lower.count(' or ') > 1
        
        # Calculate Final Score (0-100)
        score = 0
        
        # Flesch readability (inverted: lower flesch = harder)
        if flesch_score > 70:
            score += 10  # Easy to read
        elif flesch_score > 50:
            score += 30  # Medium
        else:
            score += 50  # Hard to read
        
        # Word complexity
        if complex_ratio > 0.3:
            score += 20
        elif complex_ratio > 0.15:
            score += 10
        
        # Sentence length
        if avg_sentence_length > 20:
            score += 15
        elif avg_sentence_length > 12:
            score += 8
        
        # Question type (Bloom's taxonomy)
        score += question_type_score * 10
        
        # Number of concepts
        if potential_concepts > 5 or technical_terms > 2:
            score += 15
        elif potential_concepts > 3:
            score += 8
        
        # Negation makes it harder
        if has_negation:
            score += 10
        
        # Multiple topics
        if has_multiple_topics:
            score += 10
        
        # Determine difficulty based on total score
        if score >= 65:
            return "Advanced"
        elif score >= 35:
            return "Intermediate"
        else:
            return "Beginner"
    
    def extract_key_points(self, text):
        """Extract key points/sentences from the text"""
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        sentences = [s.strip() for s in sentences if s.strip() and len(s.split()) > 5]
        
        if not sentences:
            return []
        
        # Score each sentence based on importance
        sentence_scores = {}
        
        for sentence in sentences:
            score = 0
            words = re.findall(r'\b[a-zA-Z]{4,}\b', sentence.lower())
            
            # Count important words (not stopwords)
            important_words = [w for w in words if w not in self.stop_words]
            score += len(important_words) * 2
            
            # Bonus for technical/long words
            technical_words = [w for w in important_words if len(w) > 8]
            score += len(technical_words) * 3
            
            # Bonus for POS-like words (nouns/adjectives)
            pos_words = [w for w in important_words if self._is_likely_noun_or_adj(w)]
            score += len(pos_words) * 1.5
            
            # Penalty for very long sentences (likely less focused)
            if len(words) > 30:
                score *= 0.8
            
            sentence_scores[sentence] = score
        
        # Sort by score and select top sentences
        sorted_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Calculate how many key points to extract (3-8 based on text length)
        num_points = min(max(len(sentences) // 3, 3), 8)
        
        # Get top sentences
        key_points = [sent for sent, score in sorted_sentences[:num_points]]
        
        return key_points
    
    def process_answer(self, text):
        """Process the answer with all NLP techniques"""
        keywords = self.extract_keywords(text)
        key_points = self.extract_key_points(text)
        
        return {
            'full_answer': text,
            'summary': self.generate_summary(text),
            'keywords': keywords,
            'keyword_count': len(keywords),
            'key_points': key_points,
            'key_points_count': len(key_points),
            'paragraphs': self.create_paragraphs(text),
            'difficulty': self.predict_difficulty(text)
        }
    
    def process_question_and_answer(self, question, answer):
        """Process both question and answer"""
        keywords = self.extract_keywords(answer)
        key_points = self.extract_key_points(answer)
        
        return {
            'full_answer': answer,
            'summary': self.generate_summary(answer),
            'keywords': keywords,
            'keyword_count': len(keywords),
            'key_points': key_points,
            'key_points_count': len(key_points),
            'paragraphs': self.create_paragraphs(answer),
            'difficulty': self.analyze_question_difficulty(question),  # Based on question
            'answer_complexity': self.predict_difficulty(answer)  # Based on answer
        }