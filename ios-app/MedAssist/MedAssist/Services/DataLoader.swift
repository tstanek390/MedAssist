import Foundation

class DataLoader: ObservableObject {
    @Published var images: [MedicalImage] = []
    @Published var taxonomy: Taxonomy?
    @Published var isLoading = false
    @Published var error: String?

    func loadData() {
        isLoading = true
        error = nil

        guard let url = Bundle.main.url(forResource: "taxonomy", withExtension: "json") else {
            error = "taxonomy.json not found in app bundle"
            isLoading = false
            return
        }

        do {
            let data = try Data(contentsOf: url)
            let decoder = JSONDecoder()
            let taxonomy = try decoder.decode(Taxonomy.self, from: data)

            self.taxonomy = taxonomy
            self.images = taxonomy.images
            self.isLoading = false
        } catch {
            self.error = "Failed to load taxonomy: \\(error.localizedDescription)"
            self.isLoading = false
        }
    }
}
