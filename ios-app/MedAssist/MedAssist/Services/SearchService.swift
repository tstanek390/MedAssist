import Foundation

class SearchService: ObservableObject {
    @Published var searchText = ""
    @Published var selectedSpecialty: String?
    @Published var selectedUrgency: String?

    func filteredImages(from images: [MedicalImage]) -> [MedicalImage] {
        var results = images

        // Filter by specialty
        if let specialty = selectedSpecialty {
            results = results.filter { $0.specialty == specialty }
        }

        // Filter by urgency
        if let urgency = selectedUrgency {
            results = results.filter { $0.urgency == urgency }
        }

        // Filter by search text
        if !searchText.isEmpty {
            let query = searchText.lowercased()
            results = results.filter { image in
                image.specialty.lowercased().contains(query) ||
                image.topic.lowercased().contains(query) ||
                image.urgency.lowercased().contains(query) ||
                image.useCase.lowercased().contains(query) ||
                image.contentSummary.lowercased().contains(query) ||
                image.keyConcepts.contains(where: { $0.lowercased().contains(query) })
            }
        }

        return results
    }

    func clearFilters() {
        searchText = ""
        selectedSpecialty = nil
        selectedUrgency = nil
    }
}
