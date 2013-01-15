import java.io.File;
import java.io.IOException;
import org.apache.pig.pigunit.PigTest;
import org.apache.pig.tools.parameters.ParseException;
import org.junit.Test;

public class TestFlattenAndFilterCompanies {
    private PigTest test;

    private static final String SCRIPT = "flatten_and_filter_companies.pig";

    @Test public void testOnTestData() throws IOException, ParseException {
	String[] args = {
	    "flatten_cmd=md_flatten_companies",
	    "crunchbase_companies=../test_data/crunchbase_companies",
	    "companies=companies",
	};
	PigTest test = new PigTest(SCRIPT, args);
	test.assertOutput(new File("../test_data/companies.expected"));
    }
}
