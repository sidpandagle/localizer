# Localization Text Manager

A Python desktop application built with Tkinter for managing and translating localization text files.

## Features

- **File Input/Output**: Browse and select input/output file locations
- **Multi-line Text Editor**: Enter/paste localization keys in key=value format
- **Language Selection**: Choose from 12 supported target languages
- **Batch Translation**: Translate multiple keys at once using Google Translate API
- **UTF-8 Support**: Proper encoding for international characters
- **Error Handling**: Graceful handling of translation failures and invalid input
- **Progress Tracking**: Real-time status updates and progress indication

## Supported Languages

- French
- Spanish  
- German
- Italian
- Portuguese
- Russian
- Chinese (Simplified)
- Japanese
- Korean
- Arabic
- Hindi
- Dutch

## Installation

1. Install Python 3.6 or higher
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python localizer_gui.py
   ```

2. **Input Localization Keys**: Enter or paste your localization keys in the text area using the format:
   ```
   test.okay=Okay
   test.cancel=Cancel
   app.welcome=Welcome to our application
   ```

3. **Select Target Language**: Choose your desired target language from the dropdown menu

4. **Choose Output File**: Browse and select where you want to save the translated file

5. **Translate**: Click "Translate & Save" to start the translation process

## Input Format

The application expects localization keys in the following format:
```
key.name=Value to translate
another.key=Another value
```

- Keys remain unchanged during translation
- Only values are translated
- Comments (lines starting with #) are ignored
- Invalid format lines are skipped with warnings

## Output

The application appends translated entries to the output file in the same key=value format:
```
test.okay=d'accord
test.cancel=Annuler
app.welcome=Bienvenue dans notre application
```

## Error Handling

- Invalid input format warnings
- Translation API failure handling
- File access error handling
- Network connectivity issues
- Progress indication for long operations

## Requirements

- Python 3.6+
- tkinter (usually included with Python)
- googletrans==4.0.0rc1

## Notes

- The application uses Google Translate API through the googletrans library
- Internet connection required for translation
- Large batches may take some time to process
- Translations are appended to the output file (existing content is preserved)