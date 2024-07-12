import jakarta.xml.bind.JAXBContext;
import jakarta.xml.bind.JAXBException;
import jakarta.xml.bind.Unmarshaller;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;

import javax.wsdl.Definition;
import javax.wsdl.WSDLException;
import javax.wsdl.factory.WSDLFactory;
import javax.wsdl.xml.WSDLReader;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import java.io.File;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.HashSet;

public class PrintXSDPathsFromWSDL {

    public static void main(String[] args) {
        try {
            // Path to the WSDL file
            String wsdlPath = "src/main/resources/your.wsdl";
            File wsdlFile = new File(wsdlPath);

            // Create WSDL reader
            WSDLFactory factory = WSDLFactory.newInstance();
            WSDLReader reader = factory.newWSDLReader();
            Definition definition = reader.readWSDL(wsdlFile.getAbsolutePath());

            // Get types from the WSDL
            Map types = definition.getTypes().getExtensibilityElements();
            Set<String> processedSchemas = new HashSet<>();
            for (Object type : types.values()) {
                if (type instanceof javax.wsdl.extensions.schema.Schema) {
                    javax.wsdl.extensions.schema.Schema schema = (javax.wsdl.extensions.schema.Schema) type;
                    Element schemaElement = schema.getElement();
                    processSchemaElement(schemaElement, processedSchemas, wsdlFile.getParentFile());
                }
            }

        } catch (WSDLException | ParserConfigurationException | IOException | SAXException e) {
            e.printStackTrace();
        }
    }

    private static void processSchemaElement(Element schemaElement, Set<String> processedSchemas, File baseDir)
            throws ParserConfigurationException, IOException, SAXException {
        // Print the schema element's base URI
        String schemaBaseURI = schemaElement.getBaseURI();
        if (schemaBaseURI != null) {
            System.out.println(schemaBaseURI);
        }

        // Process <import> elements
        NodeList importElements = schemaElement.getElementsByTagNameNS("http://www.w3.org/2001/XMLSchema", "import");
        for (int i = 0; i < importElements.getLength(); i++) {
            Element importElement = (Element) importElements.item(i);
            String schemaLocation = importElement.getAttribute("schemaLocation");
            if (schemaLocation != null && !schemaLocation.isEmpty() && !processedSchemas.contains(schemaLocation)) {
                processedSchemas.add(schemaLocation);
                File importedSchemaFile = new File(baseDir, schemaLocation);
                processSchemaFile(importedSchemaFile, processedSchemas);
            }
        }

        // Process <include> elements
        NodeList includeElements = schemaElement.getElementsByTagNameNS("http://www.w3.org/2001/XMLSchema", "include");
        for (int i = 0; i < includeElements.getLength(); i++) {
            Element includeElement = (Element) includeElements.item(i);
            String schemaLocation = includeElement.getAttribute("schemaLocation");
            if (schemaLocation != null && !schemaLocation.isEmpty() && !processedSchemas.contains(schemaLocation)) {
                processedSchemas.add(schemaLocation);
                File includedSchemaFile = new File(baseDir, schemaLocation);
                processSchemaFile(includedSchemaFile, processedSchemas);
            }
        }
    }

    private static void processSchemaFile(File schemaFile, Set<String> processedSchemas)
            throws ParserConfigurationException, IOException, SAXException {
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        factory.setNamespaceAware(true);
        DocumentBuilder builder = factory.newDocumentBuilder();
        InputSource inputSource = new InputSource(schemaFile.getAbsolutePath());
        Element schemaElement = builder.parse(inputSource).getDocumentElement();
        processSchemaElement(schemaElement, processedSchemas, schemaFile.getParentFile());
    }
}
