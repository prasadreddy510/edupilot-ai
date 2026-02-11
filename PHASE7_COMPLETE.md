# Phase 7: Quiz System - COMPLETE ✅

**Implementation Date**: February 11, 2026
**Status**: ✅ All tasks completed successfully

---

## What Was Implemented

### 1. Quiz Service (`backend/app/services/quiz_service.py`)

Complete quiz generation and grading service with time tracking:

#### Core Features

**generate_quiz()**
- 100% AI-generated questions for maximum variety
- No template questions (unlike worksheets)
- Randomized question order every time
- Auto-calculated duration based on question count
- Difficulty-based generation

**Quiz Duration Mapping**:
```python
5 questions = 10 minutes
10 questions = 20 minutes
15 questions = 30 minutes
20 questions = 40 minutes
```

**Question Generation**:
- Exclusively MCQ and True/False (faster grading)
- Uses Claude AI with RAG context
- Fresh questions each attempt
- Prevents memorization

**grade_quiz()**
- Deterministic grading for objective questions
- Time tracking with seconds precision
- Time limit enforcement
- Average time per question calculation
- 70% passing threshold (higher than worksheets)

**calculate_improvement()**
- Tracks improvement across attempts
- Calculates best score, average score
- Shows improvement/decline from last attempt
- Identifies new best scores
- First attempt detection

---

### 2. Quiz API Endpoints (`backend/app/api/v1/endpoints/quizzes.py`)

Complete CRUD and attempt management:

#### Endpoints

**POST /api/v1/quizzes/generate** - Generate quiz
- Request: `topic_id`, `num_questions` (5/10/15/20), `difficulty`
- 100% AI questions
- Auto-calculated duration
- Randomized order

**GET /api/v1/quizzes** - List quizzes
- Filter by topic (optional)
- Shows attempt statistics
- Best score and latest score
- Total attempts count

**GET /api/v1/quizzes/{quiz_id}** - Get quiz details
- Complete quiz with questions
- Validates ownership

**POST /api/v1/quizzes/{quiz_id}/start** - Start attempt
- Creates new attempt record
- Records start time
- Returns attempt ID for tracking
- Prevents duplicate active attempts

**POST /api/v1/quizzes/{quiz_id}/submit** - Submit answers
- Request: `attempt_id`, `answers`
- Calculates time taken
- Grades all answers
- Calculates improvement metrics
- Returns graded results

**GET /api/v1/quizzes/{quiz_id}/attempts** - Get attempt history
- All completed attempts
- Ordered by most recent
- Includes improvement data

**GET /api/v1/quizzes/{quiz_id}/stats** - Get statistics
- Total attempts
- Best/average/latest scores
- Improvement trend
- Average time taken

---

### 3. Quiz Schemas (`backend/app/schemas/quiz.py`)

Pydantic models for validation:

```python
QuizGenerateRequest
  - topic_id: str
  - num_questions: int (5, 10, 15, 20)
  - difficulty: str (easy, medium, hard)

QuizResponse
  - Complete quiz with questions
  - duration_minutes, max_score
  - questions: List[Dict]

QuizListResponse
  - Simplified for listing
  - total_attempts, best_score, latest_score
  - topic_name included

QuizSubmitRequest
  - attempt_id: str
  - answers: Dict[str, str]

QuizAttemptResponse
  - score, percentage, passed
  - time_taken_seconds, time_exceeded
  - graded_answers with feedback
  - improvement_data (improvement metrics)

QuizStatsResponse
  - total_attempts, best_score, average_score
  - improvement_trend
  - average_time_seconds
```

---

### 4. Frontend Quiz API Client (`frontend/src/lib/api/quizzes.ts`)

Complete TypeScript integration:

#### Types
```typescript
Quiz {
  duration_minutes: number
  questions: QuizQuestion[]
}

QuizAttempt {
  started_at, submitted_at
  time_taken_seconds, time_exceeded
  improvement_data: ImprovementData
}

ImprovementData {
  is_first_attempt, improvement
  best_score, average_score
  total_attempts, is_best_score
}

QuizStats {
  total_attempts, best/average/latest_score
  improvement_trend
  average_time_seconds
}
```

#### Functions
- `generate()` - Generate quiz
- `list()` - Get quizzes
- `get()` - Get specific quiz
- `startAttempt()` - Start quiz attempt
- `submit()` - Submit answers
- `getAttempts()` - Get attempt history
- `getStats()` - Get statistics

---

### 5. Quizzes List Page (`frontend/src/app/(student)/quizzes/page.tsx`)

Quiz management dashboard:

#### Features
- **List All Quizzes** with metadata
- **Attempt Statistics**: Total attempts, best score, latest score
- **Duration Display**: Shows time limit per quiz
- **Click to Continue**: Opens attempts or starts new attempt
- **Empty State**: Helpful CTA for first quiz
- **Difficulty Badges**: Color-coded

---

### 6. Generate Quiz Page (`frontend/src/app/(student)/quizzes/generate/page.tsx`)

Interactive quiz creation:

#### Features
- **Subject & Topic Selection**: Cascading dropdowns
- **Difficulty Selector**: 3 buttons (Easy/Medium/Hard)
- **Quiz Size Selector**: 4 cards with durations
  - 5 questions (10 min)
  - 10 questions (20 min)
  - 15 questions (30 min)
  - 20 questions (40 min)
- **Timer Preview**: Shows calculated duration
- **Warning Info**: Explains auto-submit behavior
- **Pre-fill Support**: URL param `?topic=<id>`

---

### 7. Quiz Taking Page (`frontend/src/app/(student)/quizzes/[id]/page.tsx`)

**Most complex page with real-time timer:**

#### Start Screen
- Quiz overview (questions, duration, difficulty)
- Important warnings about timer
- "Start Quiz" button
- Cannot go back after starting

#### Quiz In Progress
**Sticky Header**:
- Quiz title
- Progress indicator (X/Y answered)
- **Countdown Timer** (updates every second)
  - Blue text when >30% time left
  - Orange text when 10-30% time left
  - Red text when <10% time left
- Submit button

**Auto-Submit Logic**:
- Timer counts down from duration
- When timer reaches 0:
  - Automatically submits answers
  - Clears interval
  - Shows "Time's up!" message
  - Redirects to results

**Question Cards**:
- MCQ: Radio buttons
- True/False: Two large buttons
- Check marks on answered questions
- Progress bar fills as questions answered

**State Management**:
- Local answers state
- Current attempt tracking
- Time remaining (updates every second)
- Auto-submit flag

---

### 8. Quiz Results Page (`frontend/src/app/(student)/quizzes/[id]/result/page.tsx`)

Comprehensive results with improvement tracking:

#### Score Card
- **Pass/Fail Banner** with gradient
- **Percentage Score**: Large display
- **Correct/Incorrect Count**
- **Time Taken**: Formatted (Xm Ys)
- **Time Status**: On time or exceeded warning

#### Improvement Section
- Shows only for repeat attempts
- **Improvement Indicator**:
  - Green up arrow if improved
  - Red down arrow if declined
  - Percentage change from last attempt
- **Statistics**:
  - Attempt number
  - Best score achieved
  - Average across all attempts
- **New Best Score Badge** (🏆 if applicable)

#### Action Buttons
- Try Again (retake quiz)
- View All Attempts (history)
- Start New Quiz (different quiz)

#### Detailed Results
- Question-by-question breakdown
- Your answer vs correct answer
- Color-coded borders (green/red)
- Simple feedback ("Correct"/"Incorrect")

---

### 9. Quiz Attempts Page (`frontend/src/app/(student)/quizzes/[id]/attempts/page.tsx`)

Complete attempt history and analytics:

#### Stats Summary (3 cards)
- **Best Score**: Highest percentage achieved
- **Average Score**: Mean of all attempts
- **Total Attempts**: Count of completed attempts

#### Attempt History
- **Attempt Cards** showing:
  - Attempt number (descending)
  - Best score badge (for highest)
  - Pass/fail indicator
  - Date and time
  - Score and percentage
  - Time taken
  - Time exceeded warning (if applicable)
  - Improvement from previous attempt

**Improvement Indicators**:
- Green ↑ with +X% if improved
- Red ↓ with -X% if declined
- Gray text if same score

---

## File Structure

```
backend/app/
├── services/
│   └── quiz_service.py                  # Quiz generation & grading
├── api/v1/endpoints/
│   └── quizzes.py                       # 7 API endpoints
└── schemas/
    └── quiz.py                          # Pydantic schemas

frontend/src/
├── app/(student)/quizzes/
│   ├── page.tsx                         # Quizzes list
│   ├── generate/
│   │   └── page.tsx                     # Generate quiz
│   ├── [id]/
│   │   ├── page.tsx                     # Take quiz (with timer)
│   │   ├── result/
│   │   │   └── page.tsx                 # View results
│   │   └── attempts/
│   │       └── page.tsx                 # Attempt history
└── lib/api/
    └── quizzes.ts                       # API client
```

---

## Technology Stack

### Backend
- **FastAPI**: REST API
- **SQLAlchemy**: Quiz and attempt storage
- **Claude AI**: 100% AI question generation
- **RAG Service**: NCERT context

### Frontend
- **Next.js 14**: App Router
- **TypeScript**: Type safety
- **React Query**: Data fetching
- **Real-time Timer**: setInterval with cleanup
- **Tailwind CSS**: Styling

---

## Data Flow

### Quiz Generation Flow

```
1. Student selects topic, difficulty, size
   ↓
2. POST /api/v1/quizzes/generate
   ↓
3. Quiz Service:
   ├─ Get RAG context for topic
   ├─ Call Claude AI (100% AI questions)
   ├─ Generate MCQ and True/False only
   ├─ Randomize question order
   └─ Calculate duration (based on count)
   ↓
4. Save quiz to database
   ↓
5. Return to frontend
   ↓
6. Redirect to quiz start screen
```

### Quiz Taking Flow

```
1. Student clicks "Start Quiz"
   ↓
2. POST /api/v1/quizzes/{id}/start
   ↓
3. Create quiz attempt with start time
   ↓
4. Return attempt_id to frontend
   ↓
5. Frontend starts countdown timer
   ├─ setInterval(() => setTimeRemaining(prev - 1), 1000)
   ├─ Updates every second
   └─ Color changes based on remaining time
   ↓
6. Student answers questions
   ├─ Local state updates
   └─ Progress bar fills
   ↓
7. Either:
   ├─ Student clicks "Submit" (manual)
   └─ Timer reaches 0 (auto-submit)
   ↓
8. POST /api/v1/quizzes/{id}/submit
   ↓
9. Calculate time_taken = now - started_at
   ↓
10. Grade quiz:
    ├─ MCQ: Exact match
    └─ True/False: Exact match
    ↓
11. Get previous attempts for improvement
    ↓
12. Calculate improvement metrics
    ↓
13. Save graded attempt
    ↓
14. Redirect to results page
```

### Timer Logic

```javascript
// Start timer when quiz begins
useEffect(() => {
  if (!hasStarted) return

  const timer = setInterval(() => {
    setTimeRemaining((prev) => {
      if (prev <= 1) {
        // Time's up!
        clearInterval(timer)
        autoSubmitRef.current = true
        submitMutation.mutate() // Auto-submit
        return 0
      }
      return prev - 1
    })
  }, 1000)

  // Cleanup on unmount
  return () => clearInterval(timer)
}, [hasStarted])

// Color coding
const getTimerColor = () => {
  const percentage = (timeRemaining / totalTime) * 100
  if (percentage <= 10) return 'text-red-600'    // Critical
  if (percentage <= 30) return 'text-orange-600' // Warning
  return 'text-blue-600'                          // Normal
}
```

---

## API Examples

### Generate Quiz

**Request:**
```bash
POST /api/v1/quizzes/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "topic_id": "550e8400-e29b-41d4-a716-446655440000",
  "num_questions": 10,
  "difficulty": "medium"
}
```

**Response:**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "title": "Photosynthesis - Medium Quiz",
  "difficulty": "medium",
  "total_questions": 10,
  "duration_minutes": 20,
  "max_score": 10,
  "questions": [
    {
      "question_number": 1,
      "type": "MCQ",
      "question": "Which gas is released during photosynthesis?",
      "options": ["Oxygen", "Carbon Dioxide", "Nitrogen", "Hydrogen"],
      "points": 1
    }
  ]
}
```

### Start Quiz Attempt

**Request:**
```bash
POST /api/v1/quizzes/660e8400-e29b-41d4-a716-446655440000/start
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440000",
  "quiz_id": "660e8400-e29b-41d4-a716-446655440000",
  "started_at": "2026-02-11T15:30:00Z",
  "answers": {}
}
```

### Submit Quiz

**Request:**
```bash
POST /api/v1/quizzes/660e8400-e29b-41d4-a716-446655440000/submit
Authorization: Bearer <token>
Content-Type: application/json

{
  "attempt_id": "770e8400-e29b-41d4-a716-446655440000",
  "answers": {
    "1": "Oxygen",
    "2": "True",
    "3": "Chlorophyll"
  }
}
```

**Response:**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440000",
  "quiz_id": "660e8400-e29b-41d4-a716-446655440000",
  "submitted_at": "2026-02-11T15:45:00Z",
  "score": 8,
  "max_score": 10,
  "percentage": 80.0,
  "passed": true,
  "time_taken_seconds": 900,
  "time_exceeded": false,
  "graded_answers": [...],
  "improvement_data": {
    "is_first_attempt": false,
    "improvement": 10.0,
    "best_score": 80.0,
    "average_score": 75.0,
    "total_attempts": 3,
    "is_best_score": true
  }
}
```

---

## Key Features

✅ **Real-Time Countdown Timer**
- Updates every second
- Color changes (blue → orange → red)
- Auto-submit at zero
- Cleanup on unmount

✅ **100% AI Questions**
- Fresh questions every time
- No template reuse
- Maximum variety
- Prevents memorization

✅ **Improvement Tracking**
- Comparison to previous attempts
- Best score highlighting
- Average score calculation
- Visual improvement indicators

✅ **Time Tracking**
- Accurate to the second
- Time exceeded warnings
- Average time per question
- Duration based on question count

✅ **Multiple Attempts**
- Unlimited retakes
- Each attempt saved
- History tracking
- Statistical analysis

✅ **Auto-Submit**
- Timer enforcement
- Graceful auto-submission
- User notification
- Prevents late submissions

---

## Testing the Quiz System

### 1. Generate Quiz

```bash
# Start services
cd backend && uvicorn app.main:app --reload
cd frontend && npm run dev
```

1. Navigate to http://localhost:3000/student/quizzes
2. Click "Start New Quiz"
3. Select topic, difficulty, size (e.g., 10 questions = 20 min)
4. Click "Start Quiz"

### 2. Take Quiz

1. Review quiz overview
2. Click "Start Quiz" (timer begins immediately)
3. Watch countdown timer in header
4. Answer questions (MCQ or True/False)
5. See progress bar fill up
6. Either:
   - Click "Submit Quiz" early
   - Wait for timer to reach 0 (auto-submit)

### 3. View Results

1. See score card with percentage
2. Check if passed (70%+)
3. Review improvement section (if repeat attempt)
4. View detailed question breakdown
5. Click "Try Again" to retake

### 4. View Attempt History

1. Click "View All Attempts"
2. See stats summary (best/average/total)
3. Review each attempt card
4. Check improvement indicators
5. Identify best attempt (🏆 badge)

### 5. Verify Timer Auto-Submit

1. Start quiz but don't answer
2. Wait for timer to reach 0:00
3. Should see "Time's up!" toast
4. Should auto-redirect to results
5. Check "Time Exceeded" warning in results

---

## Performance Optimizations

### Backend
- **AI-Only Questions**: Faster generation (no template lookup)
- **Deterministic Grading**: Instant for MCQ/True-False
- **Improvement Caching**: Previous attempts fetched once
- **Index Optimization**: Fast attempt queries

### Frontend
- **Local State**: Answers stored locally
- **Optimistic Updates**: Immediate UI feedback
- **Timer Cleanup**: Prevents memory leaks
- **React Query**: Caches quiz data

---

## Statistics & Metrics

### Backend
- **Service**: 1 major service (280+ lines)
- **Endpoints**: 7 API routes
- **Schemas**: 7 Pydantic models
- **Auto-Submit**: Timer-based enforcement

### Frontend
- **Pages**: 5 complete pages
- **Timer**: Real-time countdown with auto-submit
- **Lines of Code**: ~1,400 frontend lines

### Features
- ✅ Real-time countdown timer
- ✅ Auto-submit on timeout
- ✅ 100% AI question generation
- ✅ Multiple attempts with tracking
- ✅ Improvement metrics
- ✅ Time tracking to the second
- ✅ 70% passing threshold
- ✅ Attempt history with stats

---

## What Works Now

✅ Generate timed quizzes with AI questions
✅ Real-time countdown timer (updates every second)
✅ Auto-submit when timer reaches zero
✅ Start quiz attempt with time tracking
✅ Submit quiz with time limit enforcement
✅ Multiple attempts allowed
✅ Improvement tracking across attempts
✅ Best score highlighting
✅ Attempt history with statistics
✅ Time exceeded warnings
✅ Color-coded timer (blue/orange/red)
✅ MCQ and True/False questions only
✅ 70% passing grade
✅ Comprehensive results page
✅ Responsive design

---

## Success Criteria - All Met! ✅

- ✅ Quiz generation service
- ✅ 100% AI question generation
- ✅ Randomized question order
- ✅ Auto-calculated duration
- ✅ Start quiz attempt endpoint
- ✅ Submit quiz with time tracking
- ✅ Real-time countdown timer
- ✅ Auto-submit on timeout
- ✅ Multiple attempts allowed
- ✅ Improvement tracking
- ✅ Attempt history
- ✅ Quiz statistics
- ✅ Timer color coding
- ✅ Results page with improvement
- ✅ All UI pages complete

---

## What's Next - Phase 8: Doubt Chatbot

Phase 8 will implement:

1. **Chatbot Interface**
   - Real-time messaging
   - LaTeX/math rendering
   - Code highlighting
   - Message history

2. **AI Integration**
   - RAG-enhanced responses
   - Conversation context
   - Source attribution
   - Follow-up handling

3. **Conversation Management**
   - Create/list conversations
   - Topic-based threads
   - Search conversations

---

## Phase 7 Status: ✅ COMPLETE

The Quiz System is fully functional with:
- Real-time countdown timer with auto-submit
- 100% AI-generated questions for variety
- Multiple attempts with improvement tracking
- Comprehensive attempt history and analytics
- Professional, polished UI

**Ready to proceed to Phase 8: Doubt Chatbot!**
