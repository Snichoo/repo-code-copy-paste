```markdown
# Simple Repo Viewer

A lightweight web application that allows you to browse and view the contents of files in your local repositories with real-time change detection.

## Key Features

- **Simple File Navigation**: Just enter the path to your repository, and it will display all files and folders in a tree structure
- **Selective File Viewing**: Choose specific files you want to examine, and view their contents with file paths clearly marked
- **Real-time Change Detection**: Automatically detects changes in the folder structure and notifies you
- **Easy-to-use Interface**: Clean and intuitive UI with folder expansion/collapse functionality

## Use Cases

1. **Code Review**: Quickly view multiple files from a repository without having to open them individually
2. **Documentation Generation**: Select multiple files to compile their contents into a single view
3. **File System Monitoring**: Keep track of changes in your repository structure
4. **Content Aggregation**: Combine contents from multiple files for analysis or documentation

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/repo-viewer.git
```

2. Install the required dependencies:
```bash
pip install flask
```

## Usage

1. Run the Flask application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Enter the path to your repository in the input field
4. Click "Load Folder" to view the file structure
5. Select the files you want to view
6. Click "Confirm" to see the contents of selected files

## Features in Detail

### File Tree Navigation
- Expandable/collapsible folder structure
- Checkbox selection for files
- Clear visual hierarchy of folders and files

### Content Display
- File contents are displayed with clear file path headers
- Multiple file contents are combined in a single view
- UTF-8 encoding support with fallback error handling

### Change Detection
- Automatic polling every 10 seconds
- Visual notification when changes are detected
- One-click update to reflect changes

## Technical Details

- Built with Flask (Python)
- Pure JavaScript frontend (no external dependencies)
- Real-time file system monitoring
- Responsive design

## Security Considerations

- The application runs locally and accesses local files
- Implement additional security measures before deploying in a production environment
- Be cautious with file permissions when using in shared environments

```