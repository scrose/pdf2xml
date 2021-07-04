<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" doctype-system="submissionmanifest.4.1.dtd"
    doctype-public="-//Atypon//DTD Literatum Content Submission Manifest DTD v4.1 20100405//EN"/>

    <xsl:template match="/">
      <submission group-doi="{/root/publication/doi}" submission-type="full" />
    </xsl:template>

</xsl:stylesheet>
