# Knowledge Task Feature Documentation

## Overview

The Knowledge Task feature is a smart content delivery system that provides users with educational content based on their active habits and learning progress. The system intelligently selects appropriate knowledge items and tracks user engagement through a multi-step learning process with quizzes and rewards.

## Architecture

### Core Components

- **Knowledge Base**: Stores knowledge content items with associated metadata
- **User Progress Tracking**: Monitors user consumption and completion status
- **Habit Integration**: Links knowledge content to specific habit blueprints
- **Content Delivery Logic**: Intelligent selection algorithm for personalized content

### API Endpoints

#### 1. `GET /knowledge-items/{userId}` - Fetch Knowledge Item for User

**File**: `apis/info-content/v1/fetch_knowledge_item_for_user.ts`

**Purpose**: Retrieves the next appropriate knowledge item for a user based on their profile, habits, and consumption history.

**Algorithm Flow**:
1. **User Profile Validation**: Fetch and validate user profile
2. **Daily Consumption Check**: Verify if user has already consumed content today (prevents multiple items per day)
3. **Active Habits Analysis**: Identify today's active habits for the user
4. **Habit-Based Content Selection**: Search for knowledge items related to active habit blueprints
5. **Generic Content Fallback**: If no habit-specific content available, select from generic knowledge items
6. **Completion Filtering**: Exclude already completed content

**Response**: Returns an array containing either:
- One knowledge item (habit-specific or generic)
- Empty array if no suitable content or daily limit reached

#### 2. `PUT /knowledge-items` - Update Knowledge Item Progress

**File**: `apis/info-content/v1/update_knowledge_item_for_user.ts`

**Purpose**: Updates user progress on a knowledge item, tracking steps completed, quiz answers, and completion status.

**Functionality**:
- Creates new progress record if none exists
- Updates existing progress with current step and quiz answers
- Calculates completion status based on content steps and quiz completion
- Maintains creation and update timestamps

## Data Models

### KnowledgeBaseItem
```typescript
interface KnowledgeBaseItem {
  id: string;
  dimension: string;        // Knowledge dimension/category
  archetype: string;        // User archetype targeting
  relatedToType: 'HABITBP' | 'GENERIC';  // Content type
  relatedToId: string;      // Related habit blueprint ID or generic identifier
  jsonContent: KnowledgeBaseContent;
}
```

### KnowledgeBaseContent
```typescript
interface KnowledgeBaseContent {
  contentStepDurationInSeconds: number;
  content: KnowledgeBaseContentItem[];  // Sequential learning steps
  quiz: KnowledgeBaseQuizItem[];        // Assessment questions
  coinsReward: number;                  // Reward for completion
}
```

### UserConsumedKnowledgeItem
```typescript
interface UserConsumedKnowledgeItem {
  id: string;
  userId: string;
  knowledgeContentId: string;
  knowledgeContent: KnowledgeBaseContent;
  currentStep: number;                  // Current progress position
  didCompleteContent: boolean;          // Full content completion status
  didAnswerQuiz: boolean;              // Quiz completion status
  answeredQuiz: KnowledgeBaseQuizItem[]; // User's quiz responses
  createdAt: number;
  updatedAt: number;
}
```

## Business Logic

### Content Selection Priority
1. **Habit-Specific Content**: First priority for users with active habits
2. **Generic Content**: Fallback option for comprehensive learning
3. **Completion Awareness**: Avoids serving already completed content
4. **Daily Limits**: One knowledge item per user per day

### Completion Tracking
- **Content Completion**: When `currentStep` equals total content steps
- **Quiz Completion**: When all quiz questions are answered
- **Overall Completion**: Both content and quiz must be completed

### Habit Integration
- Fetches user's active habits for the current day
- Matches knowledge items to habit blueprint IDs
- Considers day-of-week frequency for habit activation
- Filters out deleted habits and those without blueprint IDs

## Database Tables

### KnowledgeBaseTable
- Stores all knowledge content items
- Indexed by `relatedToType` for efficient filtering
- Contains structured learning content and assessments

### UserConsumedKnowledgeTable
- Tracks individual user progress
- Indexed by `userId` for user-specific queries
- Composite index on `userIdKnowledgeContentId` for efficient updates

### HabitsDesignTable
- User habit configurations
- Indexed by `email` for user habit retrieval
- Contains frequency and blueprint associations

### ProfileTable
- User profile information
- Primary key: `userId`
- Contains user email and other profile data

## Key Features

### 1. Intelligent Content Delivery
- **Habit-Aware**: Prioritizes content relevant to user's active habits
- **Personalized**: Considers user archetype and learning dimension
- **Progressive**: Tracks step-by-step learning progression

### 2. Learning Assessment
- **Interactive Quizzes**: Multi-choice and single-choice questions
- **Progress Tracking**: Monitors completion of both content and assessments
- **Immediate Feedback**: Real-time progress updates

### 3. Gamification Elements
- **Coin Rewards**: Users earn coins for completing knowledge items
- **Achievement Tracking**: Completion status and progress metrics
- **Daily Engagement**: Encourages consistent daily learning

### 4. Content Management
- **Flexible Structure**: Supports various content types (text, images, videos)
- **Ordered Content**: Sequential learning with defined step progression
- **Rich Media**: Support for images, videos, and formatted text

## Error Handling

- **User Validation**: Ensures user profile exists before content delivery
- **Input Validation**: Validates required fields in update requests
- **Graceful Degradation**: Falls back to generic content when habit-specific unavailable
- **Comprehensive Logging**: Detailed console logging for debugging and monitoring

## Performance Considerations

- **Efficient Queries**: Uses DynamoDB indexes for fast data retrieval
- **Minimal Data Transfer**: Returns only necessary content structure
- **Caching Strategy**: Considers user consumption patterns for optimal delivery

## Future Enhancements

- **Content Recommendations**: ML-based content suggestion algorithms
- **Progress Analytics**: Detailed learning analytics and insights
- **Social Features**: Sharing and collaborative learning capabilities
- **Advanced Gamification**: Streaks, badges, and achievement systems
