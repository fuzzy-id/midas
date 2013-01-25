import java.io.File;
import java.io.IOException;
import org.junit.Test;
import org.junit.Ignore;
import org.apache.pig.pigunit.PigTest;
import org.apache.pig.tools.parameters.ParseException;

public class TestSplitSitesWAndWoCompanies {
    private PigTest test;
    private static final String SCRIPT = "split_sites_w_and_wo_companies.pig";

    @Test public void testSampleData() throws IOException, ParseException {
        String[] params = {
            "associations=../test_data/associations",
            "sites=../test_data/sites",
	    "companies=../test_data/companies",
	    "sites_w_company=sites_w_company",
	    "sites_wo_company=sites_wo_company",
        };

	PigTest test = new PigTest(SCRIPT, params);
	
	test.assertOutput("sites_w_company",
			  new File("../test_data/sites_w_company.expected"));
	test.assertOutput("sites_wo_company",
			  new File("../test_data/sites_wo_company.expected"));
    }
}