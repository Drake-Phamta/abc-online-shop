package vn.ptit.ecom.controller;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;
import vn.ptit.ecom.ai.SearchQuery;
import vn.ptit.ecom.service.SearchService;

/** UC04 search with the AI search (docs/SPEC.md section 6): typed or spoken text, or a photo. Guests may search. */
@RestController
public class SearchController {
    /** AI02: how the query was understood, in words the result page can show. */
    record Understood(List<String> terms, List<String> related, List<String> corrections, Long minPrice, Long maxPrice,
                      boolean cheap) {
        static Understood of(SearchQuery q) {
            List<String> related = new ArrayList<>();
            q.related().forEach((t, rels) -> related.add(t + " → " + String.join(", ", rels)));
            List<String> corrections = new ArrayList<>();
            q.corrections().forEach((from, to) -> corrections.add(from + " → " + to));
            return new Understood(q.terms(), related, corrections, q.minPrice(), q.maxPrice(), q.cheap());
        }
    }

    record Found(Views.ProductCard product, double score, List<String> reasons) { }

    record SearchView(String mode, String query, Understood understood, boolean fallback, long tookMs, List<Found> results) {
        static SearchView of(SearchService.SearchResult r) {
            return new SearchView(r.mode().name(), r.understood().text(), Understood.of(r.understood()), r.fallback(), r.tookMs(),
                    r.items().stream().map(i -> new Found(Views.ProductCard.of(i.product()), i.score(), i.reasons())).toList());
        }
    }

    private final SearchService search;

    public SearchController(SearchService search) {
        this.search = search;
    }

    @GetMapping("/api/search")
    public SearchView search(@RequestParam(required = false) String q) {
        return SearchView.of(search.search(q));
    }

    @PostMapping(value = "/api/search/photo", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public SearchView searchByPhoto(@RequestParam("photo") MultipartFile photo) throws IOException {
        return SearchView.of(search.searchByPhoto(photo.getBytes()));
    }
}
