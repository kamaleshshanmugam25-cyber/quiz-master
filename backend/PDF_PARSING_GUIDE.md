# PDF Parsing and Auto-Question Creation Guide

This guide explains how to use the new PDF parsing functionality in your Django quiz app.

## Overview

The system now supports automatic question creation from PDF files. When you upload a PDF with questions in a specific format, the system will:

1. Extract text from the PDF
2. Parse questions and answers using regex patterns
3. Automatically create Question and Choice records in the database
4. Mark the correct answers based on the "Answer:" lines

## PDF Format Requirements

Your PDF should contain questions in this exact format:

```
Q1. What is the capital of France?
A) Paris
B) London
C) Berlin
D) Rome
Answer: A

Q2. Which planet is known as the Red Planet?
A) Earth
B) Mars
C) Jupiter
D) Venus
Answer: B
```

### Format Rules:
- Questions must start with "Q" followed by a number and a period or parenthesis
- Options must be labeled A), B), C), D) (with parentheses or periods)
- Each question must have an "Answer:" line indicating the correct choice
- Questions can span multiple lines
- Empty lines between questions are allowed

## API Endpoints

### 1. Preview PDF Questions (Existing)
**POST** `/api/quiz/upload-pdf/`

Upload a PDF to preview the parsed questions without creating them in the database.

**Request:**
- `file`: PDF file (multipart/form-data)

**Response:**
```json
{
    "questions": [
        {
            "text": "What is the capital of France?",
            "timer_seconds": 20,
            "image": null,
            "choices": [
                {"text": "Paris", "is_correct": true},
                {"text": "London", "is_correct": false},
                {"text": "Berlin", "is_correct": false},
                {"text": "Rome", "is_correct": false}
            ]
        }
    ],
    "count": 1
}
```

### 2. Auto-Create Questions from PDF (New)
**POST** `/api/quiz/auto-create-questions/`

Upload a PDF and automatically create all questions and choices in the database.

**Request:**
- `file`: PDF file (multipart/form-data)
- `quiz_id`: ID of the quiz to add questions to

**Response:**
```json
{
    "message": "Successfully created 4 questions",
    "questions_created": 4,
    "quiz_id": 123,
    "questions": [
        {
            "id": 456,
            "text": "What is the capital of France?",
            "order": 1,
            "choices_count": 4
        }
    ]
}
```

## Usage Examples

### Frontend JavaScript Example

```javascript
// Auto-create questions from PDF
const autoCreateQuestions = async (quizId, pdfFile) => {
    const formData = new FormData();
    formData.append('file', pdfFile);
    formData.append('quiz_id', quizId);
    
    try {
        const response = await fetch('/api/quiz/auto-create-questions/', {
            method: 'POST',
            headers: {
                'Authorization': `Token ${localStorage.getItem('authToken')}`
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            console.log(`Created ${data.questions_created} questions`);
            // Refresh the quiz editor or redirect
        } else {
            console.error('Error:', data.error);
        }
    } catch (error) {
        console.error('Upload failed:', error);
    }
};

// Preview PDF questions
const previewPdfQuestions = async (pdfFile) => {
    const formData = new FormData();
    formData.append('file', pdfFile);
    
    try {
        const response = await fetch('/api/quiz/upload-pdf/', {
            method: 'POST',
            headers: {
                'Authorization': `Token ${localStorage.getItem('authToken')}`
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            console.log(`Found ${data.count} questions`);
            // Display preview in UI
        } else {
            console.error('Error:', data.error);
        }
    } catch (error) {
        console.error('Upload failed:', error);
    }
};
```

### Python/Django Example

```python
import requests

# Auto-create questions
def auto_create_questions(quiz_id, pdf_path, auth_token):
    url = 'http://localhost:8000/api/quiz/auto-create-questions/'
    
    with open(pdf_path, 'rb') as f:
        files = {'file': f}
        data = {'quiz_id': quiz_id}
        headers = {'Authorization': f'Token {auth_token}'}
        
        response = requests.post(url, files=files, data=data, headers=headers)
        return response.json()

# Preview questions
def preview_questions(pdf_path, auth_token):
    url = 'http://localhost:8000/api/quiz/upload-pdf/'
    
    with open(pdf_path, 'rb') as f:
        files = {'file': f}
        headers = {'Authorization': f'Token {auth_token}'}
        
        response = requests.post(url, files=files, headers=headers)
        return response.json()
```

## Error Handling

The system handles various error cases:

- **Invalid PDF**: Returns 400 if file is not a PDF
- **No text found**: Returns 400 if PDF contains no extractable text
- **No questions found**: Returns 400 if no valid questions are parsed
- **Quiz not found**: Returns 404 if quiz_id doesn't exist or user lacks permission
- **Server errors**: Returns 500 for unexpected errors

## Dependencies

Make sure to install the required packages:

```bash
pip install PyPDF2>=3.0.0 pdfplumber>=0.9.0
```

Or install from requirements.txt:

```bash
pip install -r requirements.txt
```

## Testing

Run the test script to verify the parsing works correctly:

```bash
cd quiz-master/backend
python test_pdf_parsing.py
```

This will parse sample text and display the results.

## Notes

- Questions are created with a default timer of 20 seconds
- The system preserves the order of questions as they appear in the PDF
- Only authenticated users can create questions
- Users can only add questions to quizzes they own
- The parsing is case-insensitive for question numbers and answer letters
