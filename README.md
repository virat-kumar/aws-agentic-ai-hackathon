# Dallas Student Navigator - AI-Powered Life Assistant

An intelligent AI application designed to help international students navigate life in Dallas, Texas. This solution leverages AWS services to provide comprehensive guidance on housing, groceries, transportation, legal requirements, and cultural tips.

## 🎯 Problem Statement

International students face numerous challenges when relocating to a new city like Dallas:
- Finding affordable and safe housing
- Locating grocery stores with familiar foods
- Understanding public transportation systems
- Navigating legal requirements (visa, work permits, etc.)
- Adapting to cultural differences

This AI-powered solution acts as a personal assistant to help students overcome these challenges seamlessly.

## ✨ Key Features

### 🏠 Housing Assistance
- Recommendations for student-friendly neighborhoods
- Apartment search assistance with budget considerations
- Safety information and area insights
- Housing document verification guidance

### 🛒 Grocery & Shopping
- Locate international grocery stores by cuisine type
- Price comparison for common items
- Store locations and operating hours
- Dietary requirement considerations

### 🚌 Transportation
- Public transport routes and schedules
- Uber/Lyft cost estimates for popular destinations
- Parking information for drivers
- Bike-sharing and walkability scores

### ⚖️ Legal Requirements
- Visa status checks and reminders
- Work permit eligibility guidance
- Social Security Number application process
- Tax filing assistance and deadlines

### 🌍 Cultural Integration
- Local customs and etiquette tips
- Community events and meetups
- Language learning resources
- Making local friends and connections

## 🏗️ Architecture

### AWS Services Stack

#### 1. **AWS Bedrock** (LLM)
- **Purpose**: Natural language processing and conversational AI
- **Usage**: 
  - Chatbot interface for student queries
  - Content generation for recommendations
  - Multi-language support

#### 2. **AWS SageMaker** (Backend & ML Pipeline)
- **Purpose**: Machine learning model deployment and backend services
- **Usage**:
  - Custom recommendation models
  - User preference learning
  - Data processing and feature engineering
  - Endpoint for real-time inference

#### 3. **AWS QuickSight** (Dashboard & Visualization)
- **Purpose**: Analytics and insights dashboard
- **Usage**:
  - Student activity metrics
  - Popular services analytics
  - Usage trends and patterns
  - Administrative insights

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Student Interface                       │
│           (Web App / Mobile App / Chat Interface)           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway                            │
│              (Request Routing & Authentication)              │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        ▼                                 ▼
┌──────────────────┐          ┌──────────────────────┐
│   AWS Bedrock    │          │   AWS SageMaker      │
│      (LLM)       │          │    (Backend)         │
│                  │          │  - ML Models         │
│  - Conversational│          │  - Recommendations   │
│  - Content Gen   │          │  - Data Processing   │
│  - Multi-lingual │          │  - Endpoints         │
└──────────────────┘          └──────────┬───────────┘
                                         │
                ┌────────────────────────┴────────────────────┐
                │                                              │
                ▼                                              ▼
    ┌───────────────────┐                      ┌──────────────────────┐
    │   AWS QuickSight  │                      │   AWS Services      │
    │   (Dashboard)     │                      │  - S3 (Storage)     │
    │                    │                      │  - DynamoDB (DB)   │
    │  - Analytics       │                      │  - Lambda (Logic)  │
    │  - Visualizations  │                      │  - IAM (Security)  │
    │  - Reports         │                      └──────────────────────┘
    └───────────────────┘
```

## 🚀 Getting Started

### Prerequisites

- AWS Account with appropriate permissions
- Python 3.9 or higher
- AWS CLI configured
- Node.js 18+ (for frontend, if applicable)
- Docker (optional, for containerized deployment)

### Required AWS Services Access

- AWS Bedrock (requires model access)
- AWS SageMaker
- AWS QuickSight
- AWS S3 (Data storage)
- AWS DynamoDB (User data)
- AWS Lambda (Business logic)
- AWS IAM (Security & permissions)
- AWS API Gateway (API management)
- AWS CloudWatch (Monitoring)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/aws-agentic-ai-hackathon.git
   cd aws-agentic-ai-hackathon
   ```

2. **Set up AWS credentials**
   ```bash
   aws configure
   # Enter your AWS Access Key ID
   # Enter your AWS Secret Access Key
   # Enter your default region (e.g., us-east-1)
   ```

3. **Create required AWS resources**
   ```bash
   # Deploy infrastructure using CloudFormation or Terraform
   ./scripts/deploy.sh
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your AWS credentials and configurations
   ```

## 📁 Project Structure

```
aws-agentic-ai-hackathon/
├── README.md
├── requirements.txt
├── .env.example
├── infrastructure/
│   ├── cloudformation/
│   │   ├── bedrock-setup.yml
│   │   ├── sagemaker-setup.yml
│   │   └── quicksight-setup.yml
│   └── terraform/
│       └── main.tf
├── src/
│   ├── bedrock/
│   │   ├── llm_interface.py
│   │   └── prompts.py
│   ├── sagemaker/
│   │   ├── models/
│   │   ├── training/
│   │   └── inference/
│   └── api/
│       ├── handlers/
│       └── routes.py
├── dashboard/
│   ├── quicksight/
│   │   └── data_sources.json
│   └── templates/
├── data/
│   ├── datasets/
│   └── processed/
├── scripts/
│   ├── deploy.sh
│   ├── setup_bedrock.sh
│   └── setup_sagemaker.sh
└── tests/
    ├── unit/
    └── integration/
```

## 🔧 Configuration

### AWS Bedrock Setup
1. Enable model access in AWS Bedrock console
2. Request access to Claude, Llama, or other models
3. Configure region (us-east-1 recommended)

### AWS SageMaker Configuration
- Instance types: ml.t3.medium (development), ml.c5.xlarge (production)
- Configure IAM roles for SageMaker execution
- Set up SageMaker notebook instances for development

### AWS QuickSight Setup
1. Create QuickSight account in AWS console
2. Configure data sources (S3, DynamoDB)
3. Create datasets and analyses
4. Set up dashboards with visualizations

## 💻 Usage

### Starting the Application

1. **Start the SageMaker endpoint**
   ```bash
   python src/sagemaker/inference/start_endpoint.py
   ```

2. **Initialize Bedrock conversation**
   ```bash
   python src/bedrock/llm_interface.py
   ```

3. **Launch the application**
   ```bash
   streamlit run app.py
   # or
   python main.py
   ```

### Example Queries

```
Student: "I need to find affordable housing near UT Dallas"
Agent: "I found several options near UT Dallas. Here are 3 recommendations..."

Student: "Where can I buy Chinese ingredients?"
Agent: "There are several Asian supermarkets in Dallas. Here are the closest ones..."

Student: "Can I work part-time on an F1 visa?"
Agent: "Yes, F1 students can work part-time on-campus without authorization..."
```

## 📊 Dashboard Features

Access the QuickSight dashboard to view:
- Active user statistics
- Query distribution across categories
- Most popular services
- Student satisfaction metrics
- Usage trends and patterns

## 🔒 Security

- All AWS services use IAM for authentication
- API Gateway with WAF protection
- Data encrypted at rest (S3, DynamoDB)
- Data encrypted in transit (HTTPS/TLS)
- Least privilege IAM policies
- Input validation and sanitization

## 🧪 Testing

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run all tests
pytest
```

## 📈 Monitoring & Logging

- **AWS CloudWatch**: Application logs and metrics
- **AWS Bedrock**: Model usage and performance
- **AWS SageMaker**: Endpoint metrics and inference logs
- **AWS QuickSight**: Dashboard refresh and usage metrics

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 Roadmap

- [ ] Multi-language support (Spanish, Chinese, Hindi)
- [ ] Voice input/output integration
- [ ] Mobile app development
- [ ] Real-time housing alert system
- [ ] Community forum integration
- [ ] Integration with university systems
- [ ] Mental health resources
- [ ] Emergency contacts and services

## 🛠️ Troubleshooting

### Common Issues

**Bedrock access denied**
- Ensure model access is granted in AWS Bedrock console
- Check IAM permissions for Bedrock invoke

**SageMaker endpoint errors**
- Verify instance is running
- Check CloudWatch logs for details
- Ensure proper IAM role attached

**QuickSight connection issues**
- Verify data source permissions
- Check S3 bucket access policies
- Ensure data source is properly formatted

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- AWS Bedrock team for LLM capabilities
- AWS SageMaker for ML infrastructure
- AWS QuickSight for analytics
- Dallas student community for feedback and testing

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Contact: support@dallasstudentnavigator.com
- Documentation: https://docs.dallasstudentnavigator.com

---

Built with ❤️ for international students in Dallas
