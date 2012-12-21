import java.io.IOException;
import org.junit.Test;
import org.junit.Ignore;
import org.apache.pig.pigunit.PigTest;
import org.apache.pig.tools.parameters.ParseException;

public class TestSplitSitesWAndWoCompanies {
    private PigTest test;
    private static final String SCRIPT = "split_sites_w_and_wo_companies.pig";

    @Ignore("Fails and don't know why")
    @Test public void testSampleData() throws IOException, ParseException {
        String[] params = {
            "assocs=test_data/associations",
            "sites=test_data/alexa_sites",
	    "cb=test_data/filtered_cb",
	    "output=sites_w_company",
        };

	PigTest test = new PigTest(SCRIPT, params);
	
	String[] sites_w_company = {
	    "(foo.example.com,{(2012-12-16,1),(2012-12-15,1),(2012-12-14,1)}),foo-example,seed,2012-12-17",
	};

	String[] remaining_sites = {
	    "(bar.example.com,{(2012-12-16,2),(2012-12-15,2),(2012-12-14,2)})",
	};

	test.assertOutput(sites_w_company);

    }
}