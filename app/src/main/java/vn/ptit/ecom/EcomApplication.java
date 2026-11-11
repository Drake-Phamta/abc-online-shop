package vn.ptit.ecom;

import java.nio.file.Path;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import vn.ptit.ecom.dao.Database;
import vn.ptit.ecom.integration.CardProvider;
import vn.ptit.ecom.integration.SimulatedCardProvider;

/** Composition root: wires the database and the payment provider into the controllers. */
@SpringBootApplication
public class EcomApplication {

    public static void main(String[] args) {
        SpringApplication.run(EcomApplication.class, args);
    }

    /** abc.db.reset=true recreates the database from db/schema.sql and db/seed.sql (demo start). */
    @Bean
    Database database(@Value("${abc.db.file}") String file, @Value("${abc.db.reset:false}") boolean reset) {
        Database db = new Database(Path.of(file));
        db.create(reset);
        return db;
    }

    @Bean
    CardProvider cardProvider() {
        return new SimulatedCardProvider();
    }
}
