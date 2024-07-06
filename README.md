# C2DS AWS Lambda Set Twilight Times

This repository contains the source code for the `C2DS-aws-lambda-set-twilight-times` Lambda function. This function is
a crucial part of the Chicken Coop Door Sensor (C2DS) project, designed to manage and monitor the opening and closing
times of a chicken coop door based on local twilight times.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Setup](#setup)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Overview

The `C2DS-aws-lambda-set-twilight-times` function queries the US Naval Observatory Clock API once a day to retrieve the
sunrise and sunset times for a specific location (latitude 35.4834, longitude -86.4603, Shelbyville, TN). These times
are then stored in a DynamoDB table called `local-twilight-table`. Other functions, like the Coop Controller Handler (
CCH), will query this table to assess the state of the coop door.

## Architecture

The architecture of the `C2DS-aws-lambda-set-twilight-times` function is straightforward:

1. **Lambda Function**: This function is triggered once a day to fetch the latest twilight times.
2. **API Call**: It makes an HTTP request to the US Naval Observatory Clock API.
3. **Data Storage**: The retrieved sunrise and sunset times are stored in the `local-twilight-table` DynamoDB table.
4. **AWS Services**: The function leverages AWS Lambda and DynamoDB services.

## Setup

### Prerequisites

Before setting up this Lambda function, ensure you have the following:

- An AWS account with access to Lambda and DynamoDB services.
- Python 3.8 or higher.
- AWS CLI installed and configured with appropriate permissions.

### Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/yourusername/C2DS-aws-lambda-set-twilight-times.git
    cd C2DS-aws-lambda-set-twilight-times
    ```

2. **Navigate to the Lambda Directory**:
    ```bash
    cd lambda
    ```

3. **Install Dependencies**:
   Create a virtual environment and install the required packages.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

4. **Deploy the Lambda Function**:
   Use the AWS CLI to deploy the Lambda function.
    ```bash
    zip -r function.zip .
    aws lambda create-function --function-name set-twilight-times \
      --zip-file fileb://function.zip --handler app.lambda_handler --runtime python3.8 \
      --role arn:aws:iam::your-account-id:role/your-lambda-execution-role
    ```

## Usage

Once deployed, the Lambda function will automatically run once a day to update the twilight times in the DynamoDB table.
You can monitor the function's execution and logs via the AWS Lambda console.

## Contributing

We welcome contributions to improve the `C2DS-aws-lambda-set-twilight-times` function. Here are some ways you can help:

- **Report Bugs**: Use the issue tracker to report bugs.
- **Fix Issues**: Look for issues that you can help with.
- **Enhancements**: Propose new features or enhancements by opening an issue.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

