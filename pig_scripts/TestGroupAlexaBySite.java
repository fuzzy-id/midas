import java.io.IOException;
import java.io.File;
import org.junit.Test;
import org.apache.pig.pigunit.PigTest;
import org.apache.pig.tools.parameters.ParseException;

public class TestGroupAlexaBySite {
    private PigTest test;
    private static final String SCRIPT = "group_alexa_by_site.pig";

    @Test public void testTestDataWithFixedOutput() throws IOException, ParseException {
	String[] args = {
	    "input=../test_data/alexa_files/",
	    "adult_sites=../test_data/adult_sites/",
	    "output=rows",
	};
	String[] expected = {
	    "(foo.example.com,{(2012-09-03,1)})",
	};
	PigTest test = new PigTest(SCRIPT, args);
	test.assertOutput("rows", expected);
    }

    @Test public void testTestData() throws IOException, ParseException {
	String[] args = {
	    "reducers=1",
	    "input=../test_data/alexa_files/",
	    "adult_sites=../test_data/adult_sites/",
	    "output=rows",
	};
	PigTest test = new PigTest(SCRIPT, args);
	test.assertOutput(new File("../test_data/alexa_grouped_by_site.expected"));
    }
}
