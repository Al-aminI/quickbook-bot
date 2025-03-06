# QuickBooks Online Chatbot Tool

A Python Flask application that utilise AI chatbot capabilities (via LangChain) to interact with QuickBooks Online through API calls. This repository provides a collection of tools to perform various QuickBooks operations, all integrated into a conversational interface.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Extending the Toolset](#extending-the-toolset)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

---

## Overview

The QuickBooks Online Chatbot Tool is designed to simplify operations with QuickBooks Online by packaging essential API calls into tools that an AI chatbot can use. With minimal code changes (typically no more than 15 lines), you can extend the functionality to support additional QuickBooks operations.

This repository includes:
- A set of tools to perform QuickBooks API operations such as retrieving company information, listing transactions, and managing categorized/uncategorized transactions.
- A fully implemented chatbot with prompting capabilities, built to integrate seamlessly with the toolset.

---

## Features

- **Company Information**: Retrieve detailed company data from QuickBooks Online.
- **Transaction Management**:
  - List all transactions.
  - Fetch uncategorized transactions.
  - Fetch categorized transactions.
  - Post categorized transactions.
- **Extensibility**: Easily add new QuickBooks Online operations with minimal code additions.
- **Chatbot Integration**: Leverages LangChain to enable conversational interactions with the toolset.
- **Project Management**: Uses UV Python for streamlined project management and execution.

---

## Architecture

The project is structured around a Flask backend that serves both the API endpoints for QuickBooks operations and the chatbot interface. Key components include:

- **Flask Application**: Manages API endpoints and server logic.
- **LangChain Integration**: Facilitates natural language processing and conversational interactions.
- **UV Python**: Provides an efficient project management and execution environment.
- **Tooling Layer**: Each QuickBooks operation is abstracted as a tool, making the system highly modular and easy to extend.

---

## Installation

### Prerequisites

- **Python 3.x** installed on your machine.
- **QuickBooks Online API Credentials**: Ensure you have the necessary API keys and credentials from QuickBooks.
- **UV Python** for project management:
  - **macOS**: Install using Homebrew:
    ```bash
    brew install uv
    ```
  - **Alternative**: Install via pip:
    ```bash
    pip install uv
    ```

### Setup

1. **Clone the Repository**
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Synchronize Project Settings (Optional)**
   Ensure all configurations are correct by running:
   ```bash
   uv sync
   ```

3. **Run the Application**
   Start the Flask server using UV Python:
   ```bash
   uv run app.py
   ```

---

## Usage

Once the application is running, you can interact with the chatbot interface to perform various QuickBooks operations. The available commands include:

- **get_company_info**: Retrieve company details.
- **list_transactions**: Get a complete list of transactions.
- **get_uncategorized_transactions**: Fetch transactions that haven't been categorized.
- **get_categorized_transactions**: Retrieve transactions that are already categorized.
- **post_categorized_transaction**: Categorize a transaction by posting the necessary details.

These commands are designed to be invoked by an AI language model, streamlining operations and reducing manual effort.

---

## Extending the Toolset

The architecture is designed for extensibility:
- **Adding New Operations**: To add a new QuickBooks Online operation, simply integrate the corresponding API call into the toolset. This process generally requires adding no more than 15 lines of code.
- **Modular Design**: Each tool is self-contained, making it easy to maintain and expand without affecting other components of the system.

---

## Contributing

Contributions are welcome! Whether you're looking to add new features or improve existing functionality, please follow these guidelines:
- Fork the repository and create a new branch for your feature or bug fix.
- Ensure your code adheres to the existing style and includes appropriate tests.
- Submit a pull request with a detailed description of your changes.

For major changes, please open an issue first to discuss what you would like to change.

---

## License

This project is licensed under the [MIT License](LICENSE). See the LICENSE file for more details.

---

## Support

If you encounter any issues or have questions, please open an issue in the repository or contact the project maintainers.

---

*Enhance your QuickBooks Online operations with an AI-powered chatbot—simple, extensible, and efficient!*
