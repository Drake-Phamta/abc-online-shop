package vn.ptit.ecom.model.product;

import java.util.List;

/** A book: a product with the attributes of the book_detail table. */
public class BookDetail extends Product {
    private final String author;
    private final String publisher;
    private final Integer pages;
    private final String language;

    public BookDetail(Product row, String author, String publisher, Integer pages, String language) {
        super(row);
        this.author = author;
        this.publisher = publisher;
        this.pages = pages;
        this.language = language;
    }

    @Override
    public DetailKind kind() { return DetailKind.BOOK; }

    @Override
    public List<Spec> specs() {
        return list(spec("Author", author), spec("Publisher", publisher),
                spec("Pages", pages == null ? null : pages.toString()), spec("Language", language));
    }

    public String getAuthor() { return author; }
    public String getPublisher() { return publisher; }
    public Integer getPages() { return pages; }
    public String getLanguage() { return language; }
}
