import Foundation

class ClaudeService: ObservableObject {
    @Published var isQuerying = false
    @Published var error: String?

    // TODO: Add your API key here or via environment variable
    private let apiKey = "YOUR_API_KEY_HERE"
    private let apiURL = "https://api.anthropic.com/v1/messages"

    struct AISearchResult {
        let filename: String
        let relevanceScore: Int
        let clinicalReasoning: String
        let specificSections: [String]
    }

    func queryImages(query: String, images: [MedicalImage]) async -> [AISearchResult] {
        guard apiKey != "YOUR_API_KEY_HERE" else {
            print("API key not configured")
            return []
        }

        isQuerying = true
        error = nil

        // Build context about available images
        let imageSummaries = images.map { img in
            [
                "filename": img.filename,
                "specialty": img.specialty,
                "topic": img.topic,
                "urgency": img.urgency,
                "use_case": img.useCase,
                "key_concepts": img.keyConcepts.joined(separator: ", "),
                "summary": img.contentSummary
            ]
        }

        let prompt = """
        You are a clinical decision support AI helping a healthcare professional find relevant medical reference images.

        The user has asked: "\\(query)"

        Available medical reference images and their content:
        \\(try! JSONSerialization.data(withJSONObject: imageSummaries).prettyPrinted())

        Task:
        1. Analyze the clinical scenario in the user's query
        2. Identify the most relevant medical images that would help address their question
        3. Rank them by relevance (most relevant first)
        4. For each relevant image, explain WHY it's relevant to this clinical scenario

        Return a JSON array of relevant images with this format:
        [
          {
            "filename": "...",
            "relevance_score": 95,
            "clinical_reasoning": "This image is relevant because...",
            "specific_sections": ["What specific parts of the image would help"]
          }
        ]

        Only include images that are actually relevant (relevance_score >= 40).
        Limit to top 10 most relevant images.
        """

        let requestBody: [String: Any] = [
            "model": "claude-sonnet-4-5-20250929",
            "max_tokens": 2048,
            "messages": [
                [
                    "role": "user",
                    "content": prompt
                ]
            ]
        ]

        guard let url = URL(string: apiURL) else {
            error = "Invalid API URL"
            isQuerying = false
            return []
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue(apiKey, forHTTPHeaderField: "x-api-key")
        request.setValue("2023-06-01", forHTTPHeaderField: "anthropic-version")

        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: requestBody)

            let (data, response) = try await URLSession.shared.data(for: request)

            guard let httpResponse = response as? HTTPURLResponse,
                  httpResponse.statusCode == 200 else {
                error = "API request failed"
                isQuerying = false
                return []
            }

            // Parse response
            let json = try JSONSerialization.jsonObject(with: data) as? [String: Any]
            let content = json?["content"] as? [[String: Any]]
            let text = content?.first?["text"] as? String ?? ""

            // Extract JSON from response
            let results = parseAIResponse(text)

            isQuerying = false
            return results

        } catch {
            self.error = error.localizedDescription
            isQuerying = false
            return []
        }
    }

    private func parseAIResponse(_ text: String) -> [AISearchResult] {
        // Extract JSON from markdown code blocks if present
        var jsonText = text
        if let start = text.range(of: "```json")?.upperBound,
           let end = text.range(of: "```", range: start..<text.endIndex)?.lowerBound {
            jsonText = String(text[start..<end]).trimmingCharacters(in: .whitespacesAndNewlines)
        }

        guard let data = jsonText.data(using: .utf8),
              let jsonArray = try? JSONSerialization.jsonObject(with: data) as? [[String: Any]] else {
            return []
        }

        return jsonArray.compactMap { dict in
            guard let filename = dict["filename"] as? String,
                  let score = dict["relevance_score"] as? Int,
                  let reasoning = dict["clinical_reasoning"] as? String else {
                return nil
            }

            let sections = dict["specific_sections"] as? [String] ?? []

            return AISearchResult(
                filename: filename,
                relevanceScore: score,
                clinicalReasoning: reasoning,
                specificSections: sections
            )
        }
    }
}

extension Data {
    func prettyPrinted() -> String {
        guard let json = try? JSONSerialization.jsonObject(with: self),
              let data = try? JSONSerialization.data(withJSONObject: json, options: .prettyPrinted),
              let string = String(data: data, encoding: .utf8) else {
            return ""
        }
        return string
    }
}
