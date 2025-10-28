# Azure OpenAI Setup Instructions

## Configure Azure OpenAI Credentials

To use Azure OpenAI with GPT-4o, you need to provide your Azure credentials:

### Step 1: Get Azure OpenAI Credentials

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to your OpenAI resource
3. Get the following information:
   - **Endpoint URL**: Found under "Keys and Endpoint"
   - **API Key**: Found under "Keys and Endpoint" (use KEY 1 or KEY 2)
   - **API Version**: Usually `2024-02-15-preview` or latest
   - **Model Name**: `gpt-4o` (or your deployment name)

### Step 2: Create .env File

Create a `.env` file in the project root:

```bash
cp env.example .env
```

### Step 3: Add Your Azure Credentials

Edit the `.env` file and add your Azure OpenAI credentials:

```bash
# Azure OpenAI Configuration (Primary LLM)
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_api_key_here
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_MODEL=gpt-4o
```

**Replace with your actual values:**
- `your-resource-name`: Your Azure OpenAI resource name
- `your_azure_api_key_here`: Your actual API key

### Step 4: Example Configuration

Example `.env` file:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://myschool.openai.azure.com/
AZURE_OPENAI_API_KEY=abc123def456ghi789jkl012mno345pqr678stu901vwx234yz567
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_MODEL=gpt-4o
```

### Step 5: Restart the Service

After updating the `.env` file, restart the Streamlit service:

```bash
sudo systemctl restart dallas-student-navigator.service
```

### Step 6: Verify It's Working

Check the service logs to ensure Azure OpenAI is initialized:

```bash
sudo journalctl -u dallas-student-navigator.service -f
```

Look for any errors related to Azure OpenAI initialization.

### Important Notes

- **Security**: Never commit your `.env` file to git (it's already in `.gitignore`)
- **Endpoint Format**: Must end with `/` (e.g., `https://resource.openai.azure.com/`)
- **Model Name**: Should match your Azure deployment name (usually `gpt-4o`)
- **Fallback**: If Azure credentials are not found, the app will use web search only

### Troubleshooting

**Issue**: "Warning: Azure OpenAI credentials not found"
- **Solution**: Check that `.env` file exists and contains correct credentials

**Issue**: "Error initializing Azure OpenAI: ..."
- **Solution**: Verify endpoint, API key, and model name are correct

**Issue**: Model not available
- **Solution**: Ensure `gpt-4o` is deployed in your Azure OpenAI resource

### Testing

Once configured, test with queries like:
- "Where can I find affordable housing in Dallas?"
- "What are good grocery stores for Asian ingredients?"
- "How do I use Dallas public transportation?"

The responses should be synthesized by GPT-4o with web search results.

