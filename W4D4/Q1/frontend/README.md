# HR Knowledge Assistant Frontend

A Next.js chat interface for the HR Knowledge Assistant that allows users to upload HR documents and ask questions about policies, benefits, and procedures.

## Features

- **Document Upload**: Upload PDF, DOCX, and TXT files
- **Chat Interface**: Ask questions about uploaded documents
- **Inline Citations**: See which documents and chunks were used to generate answers
- **Modern UI**: Clean, responsive design with loading states
- **Real-time Feedback**: Upload status and chat responses

## Prerequisites

- Node.js 18+ installed
- Backend server running on `http://localhost:8000`

## Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## Usage

1. **Upload Documents**: Click "Choose File" and select HR documents (PDF, DOCX, or TXT)
2. **Wait for Processing**: The system will chunk and index your documents
3. **Ask Questions**: Type questions about policies, benefits, procedures, etc.
4. **View Citations**: See which documents and chunks were used for each answer

## Example Questions

- "How many vacation days do I get?"
- "What's the remote work policy?"
- "What are the health insurance benefits?"
- "How do I request time off?"
- "What's the dress code policy?"

## API Integration

The frontend communicates with the backend via:
- `POST /api/upload-doc` - Upload and process documents
- `POST /api/chat` - Send questions and get answers with citations

## Configuration

The frontend is configured to proxy API requests to `http://localhost:8000`. To change this, update the `next.config.js` file.

## Building for Production

```bash
npm run build
npm start
```

## Troubleshooting

- **Upload fails**: Ensure the backend server is running on port 8000
- **Chat not working**: Check browser console for API errors
- **Styling issues**: Ensure all CSS files are properly loaded 