import org.apache.cxf.wsdl11.WSDLManager;
import org.apache.cxf.wsdl11.WSDLManagerImpl;
import org.apache.cxf.wsdl11.WSDLServiceFactory;
import org.apache.cxf.service.model.ServiceInfo;
import org.apache.cxf.service.model.SchemaInfo;

import java.io.File;
import java.net.URI;
import java.util.HashSet;
import java.util.Set;
/**
  implementation 'org.apache.cxf:cxf-rt-core:4.0.3'
    implementation 'org.apache.cxf:cxf-rt-frontend-jaxws:4.0.3'
    implementation 'org.apache.cxf:cxf-rt-bindings-xml:4.0.3'
    implementation 'org.apache.cxf:cxf-rt-wsdl:4.0.3'
    implementation 'org.apache.cxf:cxf-rt-databinding-jaxb:4.0.3'
**/
public class PrintXSDPathsFromWSDL {

    public static void main(String[] args) {
        try {
            // Path to the WSDL file
            String wsdlPath = "src/main/resources/your.wsdl";
            File wsdlFile = new File(wsdlPath);
            URI wsdlURI = wsdlFile.toURI();

            // Create WSDL manager
            WSDLManager wsdlManager = new WSDLManagerImpl();
            WSDLServiceFactory factory = new WSDLServiceFactory(wsdlManager, wsdlURI.toString());
            ServiceInfo serviceInfo = factory.create();

            // Set to track processed schemas
            Set<String> processedSchemas = new HashSet<>();

            // Process each schema in the service
            for (SchemaInfo schemaInfo : serviceInfo.getSchemas()) {
                processSchema(schemaInfo, processedSchemas);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static void processSchema(SchemaInfo schemaInfo, Set<String> processedSchemas) {
        String schemaLocation = schemaInfo.getSystemId();
        if (schemaLocation != null && !processedSchemas.contains(schemaLocation)) {
            processedSchemas.add(schemaLocation);
            System.out.println(schemaLocation);

            // Recursively process imported and included schemas
            for (SchemaInfo importedSchema : schemaInfo.getImportedSchemas()) {
                processSchema(importedSchema, processedSchemas);
            }
        }
    }
}
