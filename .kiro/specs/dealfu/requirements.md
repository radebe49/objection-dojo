# Requirements Document

## Introduction

Dealfu is an AI-powered sales simulation web application that helps users practice their sales pitch against a skeptical AI persona. The app features a "Corporate Clean" aesthetic (professional blues, crisp whites, clean sans-serif fonts) and provides real-time feedback through a dynamic Patience Meter. Users speak their pitch via browser microphone, and the AI responds with objections or agreement, ultimately determining if the user "closes the deal" or gets "hung up on."

## Glossary

- **Patience Meter**: A 0-100% progress bar representing the AI persona's willingness to continue the conversation. Starts at 50%.
- **AI Persona**: "The Skeptic CTO" - a simulated decision-maker who evaluates user pitches and responds with objections or agreement.
- **Simulation**: A single sales call session from start to win/loss condition.
- **Lobby**: The landing screen where users initiate a new simulation.
- **Deal Closed**: The win condition flag returned by the AI when the user successfully convinces the persona.
- **Web Speech API**: Browser-native speech-to-text capability for capturing user voice input.
- **SmartMemory**: LiquidMetal Raindrop's session-based conversation context storage.

## Requirements

### Requirement 1

**User Story:** As a user, I want to land on a clean lobby screen and start a simulation, so that I can begin practicing my sales pitch.

#### Acceptance Criteria

1. WHEN a user navigates to the application THEN the Lobby_Screen SHALL display a centered "Start Simulation" button with the application title "Dealfu"
2. WHEN a user clicks the "Start Simulation" button THEN the Lobby_Screen SHALL transition to the Simulation_Screen within 500 milliseconds
3. WHEN the Simulation_Screen loads THEN the System SHALL initialize the Patience_Meter at 50%
4. WHEN the Simulation_Screen loads THEN the System SHALL request microphone permission from the browser

### Requirement 2

**User Story:** As a user, I want to speak my sales pitch using a Click-to-Talk button, so that I have full control over when my speech is captured and sent.

#### Acceptance Criteria

1. WHEN the Simulation_Screen loads THEN the UI SHALL display a single large Action_Button in Idle state showing a Microphone icon
2. WHEN the user taps the Action_Button in Idle state THEN the System SHALL start recording and transition the button to Recording state with a pulsing Stop/Send icon
3. WHEN the user taps the Action_Button in Recording state THEN the System SHALL stop recording and evaluate the transcript
4. IF the transcript is empty, null, or contains only whitespace THEN the System SHALL reset the Action_Button to Idle state without sending to Backend_API
5. IF the transcript is empty THEN the System SHALL display a toast message "I didn't hear anything." and NOT deduct patience points
6. IF the transcript contains valid text THEN the System SHALL immediately send it to the Backend_API
7. WHILE the Action_Button is in Recording state THEN the Web_Speech_API SHALL transcribe speech to text in real-time
8. IF the browser does not support Web_Speech_API THEN the System SHALL display an error message recommending Chrome or Edge browser

### Requirement 3

**User Story:** As a user, I want the AI to evaluate my pitch and respond with voice, so that I can learn from realistic objections with minimal latency.

#### Acceptance Criteria

1. WHEN the Backend_API receives user transcript THEN the Backend_API SHALL send the text to Cerebras_API with conversation context
2. WHEN Cerebras_API returns the AI response THEN the Backend_API SHALL immediately call ElevenLabs_API to generate audio from the response text
3. WHEN calling ElevenLabs_API THEN the Backend_API SHALL request MP3 format with 128kbps bitrate for optimal size and browser compatibility
4. WHEN ElevenLabs_API returns audio THEN the Backend_API SHALL encode the MP3 audio as base64
5. WHEN the Backend_API completes processing THEN the Backend_API SHALL return a single JSON response containing ai_text, patience_score, deal_closed, and audio_base64 fields
6. WHEN the Frontend receives the response THEN the System SHALL create an Audio element with data URI "data:audio/mpeg;base64,{audio_base64}" and play it

### Requirement 4

**User Story:** As a user, I want to see my progress through a Patience Meter, so that I understand how well my pitch is performing.

#### Acceptance Criteria

1. WHEN the Backend_API returns a response THEN the Frontend SHALL update the Patience_Meter to the patience_score value from the response
2. WHEN the patience_score increases THEN the UI SHALL animate the meter with a green highlight over 300 milliseconds
3. WHEN the patience_score decreases THEN the UI SHALL animate the meter with a red highlight over 300 milliseconds
4. WHEN the Patience_Meter is displayed THEN the UI SHALL show the current percentage value numerically
5. WHEN the Backend_API calculates patience_score THEN the Backend_API SHALL apply +15 for positive sentiment and -20 for negative sentiment to the current score

### Requirement 5

**User Story:** As a user, I want clear win and loss conditions, so that I know when I have succeeded or failed the simulation.

#### Acceptance Criteria

1. WHEN the Patience_Meter reaches 0% THEN the System SHALL end the simulation and display the Game_Over_Screen with "Call Failed" message
2. WHEN the Patience_Meter reaches 100% THEN the System SHALL end the simulation and display the Win_Screen with "Sale Closed" message
3. WHEN the AI response contains deal_closed equals true THEN the System SHALL end the simulation and display the Win_Screen with confetti animation
4. WHEN the Game_Over_Screen displays THEN the UI SHALL show a "Try Again" button to return to the Lobby_Screen
5. WHEN the Win_Screen displays THEN the UI SHALL show a "Play Again" button to return to the Lobby_Screen

### Requirement 6

**User Story:** As a user, I want the app to prevent audio feedback loops, so that the AI voice doesn't get picked up by my microphone.

#### Acceptance Criteria

1. WHILE the System is playing AI audio THEN the Action_Button SHALL be disabled and visually greyed out
2. WHEN the audio playback completes via the onEnded event THEN the Action_Button SHALL become enabled and return to Idle state
3. WHILE the Action_Button is disabled THEN the System SHALL ignore any tap events on the button
4. WHEN the Action_Button transitions from disabled to enabled THEN the UI SHALL provide subtle visual feedback indicating readiness

### Requirement 7

**User Story:** As a user, I want the app to handle network errors gracefully, so that technical issues don't unfairly end my simulation.

#### Acceptance Criteria

1. IF the Backend_API request fails THEN the System SHALL display a toast notification with message "Connection unstable. Say that again?"
2. IF an API error occurs THEN the System SHALL NOT deduct points from the Patience_Meter
3. WHEN a network error toast displays THEN the toast SHALL auto-dismiss after 3 seconds
4. WHEN a network error occurs THEN the System SHALL re-enable the Action_Button to allow retry

### Requirement 8

**User Story:** As a user, I want a mobile-first responsive design, so that I can practice my pitch from any device.

#### Acceptance Criteria

1. WHEN the application loads on a mobile device THEN the UI SHALL display all elements without horizontal scrolling
2. WHEN the application loads THEN the UI SHALL use a "Corporate Clean" design with professional blue (#0066CC) and white (#FFFFFF) color scheme
3. WHEN the application loads THEN the UI SHALL use clean sans-serif typography (Inter or system fonts)
4. WHEN UI elements animate THEN the animations SHALL use Framer Motion with subtle, professional transitions

### Requirement 9

**User Story:** As a developer, I want the backend to maintain conversation context within a session, so that the AI can provide coherent responses.

#### Acceptance Criteria

1. WHEN the Simulation_Screen loads THEN the Frontend SHALL generate a unique session_id using crypto.randomUUID and store it in component state
2. WHEN the Frontend sends a message to Backend_API THEN the request payload SHALL include the session_id field
3. WHEN the Backend_API receives a request THEN the Backend_API SHALL use the session_id to look up conversation history in SmartMemory
4. WHEN the user sends a message THEN the Backend_API SHALL store the message in the SmartMemory bucket identified by session_id
5. WHEN the AI responds THEN the Backend_API SHALL store the response in the SmartMemory bucket identified by session_id
6. WHEN Cerebras_API is called THEN the Backend_API SHALL include the full conversation history from the session-specific SmartMemory bucket in the prompt

### Requirement 10

**User Story:** As a developer, I want the AI to return structured JSON responses, so that the frontend can reliably parse sentiment and deal status.

#### Acceptance Criteria

1. WHEN Cerebras_API is prompted THEN the prompt SHALL instruct the model to return valid JSON with text, sentiment, and deal_closed fields
2. WHEN Cerebras_API returns a response THEN the Backend_API SHALL validate the JSON structure before forwarding
3. IF Cerebras_API returns invalid JSON THEN the Backend_API SHALL retry the request up to 2 times
4. WHEN the response is validated THEN the sentiment field SHALL contain one of: "positive", "negative", or "neutral"
5. WHEN the response is validated THEN the deal_closed field SHALL contain a boolean value

### Requirement 11

**User Story:** As a developer, I want a clean monorepo structure, so that the codebase is maintainable and deployable.

#### Acceptance Criteria

1. WHEN the project is structured THEN the repository SHALL contain a /frontend folder for the Next.js application
2. WHEN the project is structured THEN the repository SHALL contain a /backend folder for the FastAPI application
3. WHEN the frontend is configured THEN the application SHALL use Next.js 14 with App Router
4. WHEN the frontend is configured THEN the application SHALL use Tailwind CSS for styling
5. WHEN the backend is configured THEN the application SHALL use Python FastAPI with async endpoints
