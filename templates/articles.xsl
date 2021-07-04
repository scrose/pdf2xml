<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" doctype-system="BITS-book-oasis2.dtd"
    doctype-public="-//NLM//DTD BITS Book Interchange DTD with OASIS and XHTML Tables v2.0 20151225//EN"/>

    <xsl:template match="@*|node()">
      <xsl:copy>
        <xsl:apply-templates select="@*|node()"/>
      </xsl:copy>
    </xsl:template>

    <!-- import single article stylesheet -->
    <xsl:import href="article.xsl"/>

    <!-- generate article metadata -->
    <xsl:template match="/">
      <xsl:for-each select="/root/sessions">
        <xsl:for-each select="articles">
          <xsl:result-document href="{id}.xml">
            <xsl:apply-imports/>
          </xsl:result-document>
        </xsl:for-each>
      </xsl:for-each>
    </xsl:template>

  </xsl:stylesheet>
