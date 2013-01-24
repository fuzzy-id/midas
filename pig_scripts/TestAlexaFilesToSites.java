import java.io.IOException;
import java.io.File;
import org.junit.Test;
import org.apache.pig.pigunit.PigTest;
import org.apache.pig.tools.parameters.ParseException;

public class TestAlexaFilesToSites {
    private PigTest test;
    private static final String SCRIPT = "alexa_files_to_sites.pig";

    @Test public void testTestDataWithFixedOutput() throws IOException, ParseException {
	String[] args = {
	    "alexa_files=../test_data/alexa_files/",
	    "adult_sites=../test_data/adult_sites/",
	    "sites=sites",
	};
	String[] expected = {
	    "(foo.example.com,{(2012-09-03,1)})",
	};
	PigTest test = new PigTest(SCRIPT, args);
	test.assertOutput("rows", expected);
    }

    @Test public void testTestData() throws IOException, ParseException {
	String[] args = {
	    "alexa_files=../test_data/alexa_files/",
	    "adult_sites=../test_data/adult_sites/",
	    "sites=sites",
	};
	PigTest test = new PigTest(SCRIPT, args);
	test.assertOutput(new File("../test_data/sites.expected"));
    }
}
