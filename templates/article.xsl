<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" doctype-system="BITS-book-oasis2.dtd"
    doctype-public="-//NLM//DTD BITS Book Interchange DTD with OASIS and XHTML Tables v2.0 20151225//EN"/>

    <xsl:template match="/">
      <book-part-wrapper dtd-version="2.0"  xml:lang="en" content-type="research-article"  xmlns:xlink="http://www.w3.org/1999/xlink" >
        <collection-meta  collection-type="book-series">
          <collection-id collection-id-type="doi"><xsl:value-of select="root/publication/collection_id" /></collection-id>
          <title-group>
            <title><xsl:value-of select="root/publication/collection" /></title>
          </title-group>
        </collection-meta>
        <book-meta>
          <book-id book-id-type="acm-id"><xsl:value-of select="root/publication/acm_id" /></book-id>
          <book-id book-id-type="doi"><xsl:value-of select="root/publication/doi" /></book-id>
          <book-title-group>
            <book-title><xsl:value-of select="root/publication/title" /></book-title>
            <alt-title alt-title-type="acronym"><xsl:value-of select="conference/acronym" /></alt-title>
          </book-title-group>
        </book-meta>
        <book-part book-part-type="chapter" xml:lang="en">
          <book-part-meta>
            <book-part-id book-part-id-type="acm-id"><xsl:value-of select="doi" /></book-part-id>
            <book-part-id book-part-id-type="doi"><xsl:value-of select="root/publication/doi" />.<xsl:value-of select="/root/doi" /></book-part-id>
            <subj-group subj-group-type="ccs2012">
              <xsl:for-each select="root/concepts/element">
                <compound-subject>
                  <compound-subject-part content-type="code"><xsl:value-of select="id" /></compound-subject-part>
                  <compound-subject-part content-type="text"><xsl:value-of select="description" /></compound-subject-part>
                  <compound-subject-part content-type="weight"><xsl:value-of select="significance" /></compound-subject-part>
                </compound-subject>
              </xsl:for-each>
            </subj-group>
            <title-group>
              <title><xsl:value-of select="root/title" /></title>
            </title-group>
            <contrib-group>
              <xsl:for-each select="root/authors/element">
                <xsl:variable name="art_seq_no">artseq-<xsl:number format="00001"><xsl:value-of select="seq_no" /></xsl:number></xsl:variable>
                <contrib contrib-type="author" id="{$art_seq_no}">
                  <name>
                    <surname><xsl:value-of select="last_name" /></surname>
                    <given-names>
                      <xsl:value-of select="first_name" />
                      <xsl:if test="middle_name != ''">
                        <xsl:text> </xsl:text><xsl:value-of select="middle_name" />
                      </xsl:if>
                    </given-names>
                  </name>
                  <suffix><xsl:value-of select="suffix" /></suffix>
                  <aff><xsl:value-of select="affiliation" /></aff>
                  <email><xsl:value-of select="email" /></email>
                  <role><xsl:value-of select="role" /></role>
                </contrib>
              </xsl:for-each>
            </contrib-group>
            <pub-date date-type="publication">
              <day><xsl:value-of select="root/publication/date/day" /></day>
              <month><xsl:value-of select="root/publication/date/month" /></month>
              <year><xsl:value-of select="root/publication/date/year" /></year>
            </pub-date>
            <fpage><xsl:value-of select="root/page_from" /></fpage>
            <lpage><xsl:value-of select="root/page_to" /></lpage>
            <self-uri content-type="external" xlink:href="{root/url}"></self-uri>
            <abstract>
              <p><xsl:value-of select="root/abstract" /></p>
            </abstract>
            <kwd-group>
              <xsl:for-each select="root/keywords/element">
                <kwd><xsl:value-of select="kw" /></kwd>
              </xsl:for-each>
            </kwd-group>
          </book-part-meta>
          <back>
            <ref-list specific-use="unparsed">
              <xsl:for-each select="root/references/element">
                <xsl:variable name="ref_id">ref-<xsl:number format="00001"><xsl:value-of select="ref_seq_no" /></xsl:number></xsl:variable>
              <ref id="{$ref_id}">
                <mixed-citation><xsl:value-of select="ref_text" /></mixed-citation>
              </ref>
            </xsl:for-each>
          </ref-list>
        </back>
      </book-part>
    </book-part-wrapper>
  </xsl:template>

</xsl:stylesheet>
