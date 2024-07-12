import javax.wsdl.Definition;
import javax.wsdl.WSDLException;
import javax.wsdl.factory.WSDLFactory;
import javax.wsdl.xml.WSDLReader;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import java.io.File;
import java.io.IOException;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class PrintXSDPathsFromWSDL {

    public static void main(String[] args) {
        try {
            // Path to the WSDL file
            String wsdlPath = "src/main/resources/wsdl/files/avc.wsdl";
            File wsdlFile = new File(wsdlPath);

            // Create WSDL reader
            WSDLFactory factory = WSDLFactory.newInstance();
            WSDLReader reader = factory.newWSDLReader();
            Definition definition = reader.readWSDL(wsdlFile.getAbsolutePath());

            // Get types from the WSDL
            Map<?, ?> types = definition.getTypes().getExtensibilityElements();
            Set<String> referencedSchemas = new HashSet<>();
            Set<String> processedSchemas = new HashSet<>();
            for (Object type : types.values()) {
                if (type instanceof javax.wsdl.extensions.schema.Schema) {
                    javax.wsdl.extensions.schema.Schema schema = (javax.wsdl.extensions.schema.Schema) type;
                    Element schemaElement = schema.getElement();
                    processSchemaElement(schemaElement, referencedSchemas, processedSchemas, wsdlFile.getParentFile());
                }
            }

            // Base directory for XSD files
            File baseDir = new File("src/main/resources");

            // Remove leftover XSD files
            removeLeftoverXSDs(baseDir, referencedSchemas);

        } catch (WSDLException | ParserConfigurationException | IOException | SAXException e) {
            e.printStackTrace();
        }
    }

    private static void processSchemaElement(Element schemaElement, Set<String> referencedSchemas, Set<String> processedSchemas, File baseDir)
            throws ParserConfigurationException, IOException, SAXException {
        // Process <import> elements
        NodeList importElements = schemaElement.getElementsByTagNameNS("http://www.w3.org/2001/XMLSchema", "import");
        for (int i = 0; i < importElements.getLength(); i++) {
            Element importElement = (Element) importElements.item(i);
            String schemaLocation = importElement.getAttribute("schemaLocation");
            if (schemaLocation != null && !schemaLocation.isEmpty()) {
                File importedSchemaFile = new File(baseDir, schemaLocation).getCanonicalFile();
                String absolutePath = importedSchemaFile.getAbsolutePath();
                if (!processedSchemas.contains(absolutePath)) {
                    referencedSchemas.add(absolutePath);
                    processedSchemas.add(absolutePath);
                    processSchemaFile(importedSchemaFile, referencedSchemas, processedSchemas);
                }
            }
        }

        // Process <include> elements
        NodeList includeElements = schemaElement.getElementsByTagNameNS("http://www.w3.org/2001/XMLSchema", "include");
        for (int i = 0; i < includeElements.getLength(); i++) {
            Element includeElement = (Element) includeElements.item(i);
            String schemaLocation = includeElement.getAttribute("schemaLocation");
            if (schemaLocation != null && !schemaLocation.isEmpty()) {
                File includedSchemaFile = new File(baseDir, schemaLocation).getCanonicalFile();
                String absolutePath = includedSchemaFile.getAbsolutePath();
                if (!processedSchemas.contains(absolutePath)) {
                    referencedSchemas.add(absolutePath);
                    processedSchemas.add(absolutePath);
                    processSchemaFile(includedSchemaFile, referencedSchemas, processedSchemas);
                }
            }
        }
    }

    private static void processSchemaFile(File schemaFile, Set<String> referencedSchemas, Set<String> processedSchemas)
            throws ParserConfigurationException, IOException, SAXException {
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        factory.setNamespaceAware(true);
        DocumentBuilder builder = factory.newDocumentBuilder();
        InputSource inputSource = new InputSource(schemaFile.getAbsolutePath());
        Element schemaElement = builder.parse(inputSource).getDocumentElement();
        processSchemaElement(schemaElement, referencedSchemas, processedSchemas, schemaFile.getParentFile());
    }

    private static void removeLeftoverXSDs(File baseDir, Set<String> referencedSchemas) {
        // Recursively list all XSD files in the base directory and subdirectories
        Set<File> xsdFiles = new HashSet<>();
        listAllXSDFiles(baseDir, xsdFiles);

        for (File xsdFile : xsdFiles) {
            try {
                String absolutePath = xsdFile.getAbsolutePath();
                // If the XSD file is not in the set of referenced schemas, delete it
                if (!referencedSchemas.contains(absolutePath)) {
                    if (xsdFile.delete()) {
                        System.out.println("Deleted unused XSD file: " + absolutePath);
                    } else {
                        System.out.println("Failed to delete unused XSD file: " + absolutePath);
                    }
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    private static void listAllXSDFiles(File dir, Set<File> xsdFiles) {
        File[] files = dir.listFiles();
        if (files != null) {
            for (File file : files) {
                if (file.isDirectory()) {
                    listAllXSDFiles(file, xsdFiles);
                } else if (file.getName().endsWith(".xsd")) {
                    try {
                        xsdFiles.add(file.getCanonicalFile());
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                }
            }
        }
    }
}
