# Automated Screenshot Agent

![](./assets/dance-happy.gif)

안녕하세요!👋\
이 레포지토리에서는 **바이브코딩**을 사용해 만든 **시스템 점검 자동화 에이전트**를 소개합니다.\
아래 가이드를 따라 앱을 구동하고, 원하는 웹사이트를 원하는 방식으로 테스트해보세요!

- [STEP 00 - Playwright UI 통합테스트 호출해서 매일아침 자동으로 스크린샷](./step00/README.md)
- [STEP 01 - LLM에게 테스트 시나리오 알려주면 Playwright로 알아서 테스트,스크린샷](./step01/README.md)
- [STEP 02 - Agent Workflow를 사용해서 테스트,스크린샷, 잘했는지 검증하고 재시도까지](./step02/README.md)

## 🤖 바이브 코딩 방법이 더 궁금하다면

바이브 코딩 방법이 더 궁금하다면 아래 GitHub Copilot Workshop을 따라해보세요.\
앱을 만들고 다른 언어로 마이그레이션, 컨테이너화까지 모두 진행하는 단계별 자습서입니다.\
👉👉 [`GitHub Copilot` Vibe Coding Workshop(한국어)](https://github.com/microsoft/github-copilot-vibe-coding-workshop/tree/main/localisation/ko-kr) 👈👈

## 🛠️ 사용된 기술스택이 더 궁금하다면

이 프로젝트는 다음과 같은 기술로 구성되어 있습니다.\
자세한 내용은 아래 문서를 참조하세요.

- [`Playwright` for Python](https://playwright.dev/python/docs/api/class-playwright) : 
  - Playwright는 웹브라우저 자동화 및 UI 테스트를 위한 프레임워크입니다.
  - 네트워크 유휴상태, 특정 UI 엘리먼트 로드 여부 등 UI 자동화에 꼭 필요한 다양한 '대기' 기능을 제공합니다.
  - 이 프로젝트에서는 UI 통합테스트, LLM의 브라우저 조작에 사용합니다.
- [Get started with `Azure AI Foundry`](https://learn.microsoft.com/en-us/azure/ai-foundry/quickstarts/get-started-code?tabs=azure-ai-foundry#first-run-experience) : 
  - Azure AI Foundry는 Azure 클라우드의 AI 프로비저닝 서비스입니다.
  - AI 모델을 사전학습, 서빙, Agent Workflow 등 강력한 자체 생태계를 갖추고 있습니다.
  - 이 프로젝트에서는 OpenAI사의 LLM 모델을 서빙하는 데 사용합니다.
- [Getting started with `Semantic Kernel`](https://learn.microsoft.com/en-us/semantic-kernel/get-started/quick-start-guide?pivots=programming-language-csharp): 
  - Microsoft Semantic Kernel은 경량 오픈소스 AI 프레임워크입니다.
  - AI 모델을 어플리케이션에 간편하게 통합할 수 있으며, Plugin을 기반으로 모듈식 확장 기능을 제공합니다.
  - .NET/Java/Python 생태계를 모두 지원합니다!
    > Semantic Kernel은 Azure AI Foundry뿐 아니라 Google VertexAI, Amazon Bedrock, Open AI Inference API 등 다양한 AI 서비스 제공자를 지원합니다.
- [Microsoft `Agent Framework` Quick-Start Guide](https://learn.microsoft.com/en-us/agent-framework/tutorials/quick-start?pivots=programming-language-python): 
  - Semantic Kernel의 간편함과 Autogen의 Workflow 기능을 계승한 AI 에이전트 프레임워크입니다.
  - .NET/Python 생태계를 지원합니다.
    > Agent Framework는 Azure AI Foundry뿐 아니라 Google VertexAI, Amazon Bedrock, Open AI Inference API 등 다양한 AI 서비스 제공자를 지원합니다.
