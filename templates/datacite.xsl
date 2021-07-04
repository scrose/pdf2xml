<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" />

    <xsl:template match="/">
      <resource xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://datacite.org/schema/kernel-4" xsi:schemaLocation="http://datacite.org/schema/kernel-4 http://schema.datacite.org/meta/kernel-4.3/metadata.xsd">
        <identifier identifierType="DOI">
          <xsl:value-of select="root/publication/collection_id" />/<xsl:value-of select="root/doi" />
        </identifier>
        <creators>
        <xsl:for-each select="root/authors/element">
          <creator>
            <creatorName><xsl:value-of select="last_name" />, <xsl:value-of select="first_name" /></creatorName>
            <givenName><xsl:value-of select="first_name" /></givenName>
            <familyName><xsl:value-of select="last_name" /></familyName>
            <affiliation><xsl:value-of select="affiliation" /></affiliation>
          </creator>
        </xsl:for-each>
        </creators>
        <titles>
            <title xml:lang="en-ca"><xsl:value-of select="root/title" /></title>
        </titles>
        <publisher><xsl:value-of select="root/publisher/name" /></publisher>
        <publicationYear><xsl:value-of select="root/conference/year" /></publicationYear>
        <subjects>
            <subject xml:lang="en-ca" schemeURI="http://dewey.info/" subjectScheme="dewey">000 computer science</subject>
            <xsl:for-each select="root/keywords/element">
              <subject xml:lang="en-ca" subjectScheme="keywords"><xsl:value-of select="kw" /></subject>
            </xsl:for-each>
        </subjects>
        <contributors>
        <xsl:for-each select="root/chairs/element">
            <contributor contributorType="Editor">
                <contributorName><xsl:value-of select="last_name" />, <xsl:value-of select="first_name" /></contributorName>
                <givenName><xsl:value-of select="first_name" /></givenName>
                <familyName><xsl:value-of select="last_name" /></familyName>
                <affiliation><xsl:value-of select="affiliation" /></affiliation>
            </contributor>
        </xsl:for-each>
        </contributors>
        <dates>
            <date dateType="Copyrighted"><xsl:value-of select="root/publication/copyright/year" /></date>
        </dates>
        <language>en-ca</language>
        <resourceType resourceTypeGeneral="Text">Conference Proceedings</resourceType>
        <xsl:if test="not(normalize-space(root/acm/doi)='')">
        <alternateIdentifiers>
            <alternateIdentifier alternateIdentifierType="ACM Digital Library DOI">
              <xsl:value-of select="root/acm/doi" />
            </alternateIdentifier>
        </alternateIdentifiers>
        </xsl:if>
        <relatedIdentifiers>
            <relatedIdentifier relatedIdentifierType="ISSN" relationType="IsPartOf">
            <xsl:value-of select="root/publication/issn" />
          </relatedIdentifier>
            <relatedIdentifier relatedIdentifierType="ISBN" relationType="IsPartOf">
              <xsl:value-of select="root/publication/isbn" />
            </relatedIdentifier>
        </relatedIdentifiers>
        <sizes>
            <size><xsl:value-of select="root/pages" /> pages</size>
            <size><xsl:value-of select="root/file_size" /></size>
        </sizes>
        <formats>
            <format><xsl:value-of select="root/file_format" /></format>
        </formats>
        <rightsList>
            <rights>All rights reserved. No part of the material protected by this copyright notice may be reproduced or utilized in any form, electronic or mechanical, including photocopying, recording, or by any information storage and retreival system, without written permission from the copyright owner.</rights>
        </rightsList>
        <descriptions>
            <description xml:lang="en-ca" descriptionType="SeriesInformation">
                <xsl:value-of select="root/publication/description" />
            </description>
            <xsl:if test="not(normalize-space(root/abstract)='')">
            <description xml:lang="en-ca" descriptionType="Abstract">
                <xsl:value-of select="root/abstract" />
            </description>
          </xsl:if>
        </descriptions>
    </resource>
  </xsl:template>

</xsl:stylesheet>
