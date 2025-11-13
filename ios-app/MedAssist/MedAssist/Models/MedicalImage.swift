import Foundation

struct MedicalImage: Identifiable, Codable {
    let id = UUID()
    let filename: String
    let specialty: String
    let topic: String
    let urgency: String
    let keyConcepts: [String]
    let useCase: String
    let targetAudience: String
    let contentSummary: String
    let analyzedAt: String

    enum CodingKeys: String, CodingKey {
        case filename
        case specialty
        case topic
        case urgency
        case keyConc

epts = "key_concepts"
        case useCase = "use_case"
        case targetAudience = "target_audience"
        case contentSummary = "content_summary"
        case analyzedAt = "analyzed_at"
    }

    var urgencyColor: String {
        switch urgency.lowercased() {
        case "critical": return "red"
        case "high": return "orange"
        case "medium": return "yellow"
        case "low": return "green"
        default: return "gray"
        }
    }

    var imageName: String {
        // Remove extension for SwiftUI Image lookup
        filename.components(separatedBy: ".").first ?? filename
    }
}

struct Taxonomy: Codable {
    let metadata: Metadata
    let taxonomy: TaxonomyData
    let images: [MedicalImage]

    struct Metadata: Codable {
        let generatedAt: String
        let totalImagesAnalyzed: Int
        let totalErrors: Int
        let estimatedCostUsd: Double

        enum CodingKeys: String, CodingKey {
            case generatedAt = "generated_at"
            case totalImagesAnalyzed = "total_images_analyzed"
            case totalErrors = "total_errors"
            case estimatedCostUsd = "estimated_cost_usd"
        }
    }

    struct TaxonomyData: Codable {
        let specialties: [String]
        let urgencyLevels: [String]
        let useCases: [String]
        let targetAudiences: [String]
        let keyConcepts: [String]

        enum CodingKeys: String, CodingKey {
            case specialties
            case urgencyLevels = "urgency_levels"
            case useCases = "use_cases"
            case targetAudiences = "target_audiences"
            case keyConcepts = "key_concepts"
        }
    }
}
