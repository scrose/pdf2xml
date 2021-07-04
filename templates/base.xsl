<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" doctype-system="BITS-book-oasis2.dtd"
    doctype-public="-//NLM//DTD BITS Book Interchange DTD with OASIS and XHTML Tables v2.0 20151225//EN"/>

    <xsl:template match="/">
      <book dtd-version="2.0" xml:lang="en" book-type="{root/publication/book_type}" xmlns:xlink="http://www.w3.org/1999/xlink">
        <collection-meta  collection-type="book-series">
          <collection-id collection-id-type="doi"><xsl:value-of select="root/publication/collection_id"/></collection-id>
          <title-group>
            <title><xsl:value-of select="root/publication/collection"/></title>
          </title-group>
        </collection-meta>
        <book-meta>
          <book-id book-id-type="acm-id"><xsl:value-of select="root/publication/acm_id" /></book-id>
          <book-id book-id-type="doi"><xsl:value-of select="root/publication/doi" /></book-id>
          <subj-group subj-group-type="conference-collections">
            <compound-subject>
              <compound-subject-part content-type="code"><xsl:value-of select="root/publication/code" /></compound-subject-part>
              <compound-subject-part content-type="text"><xsl:value-of select="root/conference/series" /></compound-subject-part>
            </compound-subject>
          </subj-group>
          <xsl:if test="root/publication/acmsig">
            <subj-group subj-group-type="acmsig">
              <compound-subject>
                <compound-subject-part content-type="code"><xsl:value-of select="root/publication/acmsig/code" /></compound-subject-part>
                <compound-subject-part content-type="text"><xsl:value-of select="root/publication/acmsig/text" /></compound-subject-part>
                <compound-subject-part content-type="percent"><xsl:value-of select="root/publication/acmsig/percent" /></compound-subject-part>
              </compound-subject>
            </subj-group>
          </xsl:if>
          <subj-group subj-group-type="ccs2012">
            <xsl:for-each select="root/concepts/element">
              <compound-subject>
                <compound-subject-part content-type="code"><xsl:value-of select="id" /></compound-subject-part>
                <compound-subject-part content-type="text"><xsl:value-of select="description" /></compound-subject-part>
                <compound-subject-part content-type="weight"><xsl:value-of select="significance" /></compound-subject-part>
              </compound-subject>
            </xsl:for-each>
          </subj-group>
          <subj-group subj-group-type="acceptance-rates">
            <compound-subject>
              <compound-subject-part content-type="tract_type">Main</compound-subject-part>
              <compound-subject-part content-type="total_submitted">
                <xsl:value-of select="root/conference/acceptance_rates/total_submitted" />
              </compound-subject-part>
              <compound-subject-part content-type="total_accepted">
                <xsl:value-of select="root/conference/acceptance_rates/total_accepted" />
              </compound-subject-part>
            </compound-subject>
          </subj-group>
          <book-title-group>
            <book-title><xsl:value-of select="root/publication/title" /></book-title>
            <alt-title alt-title-type="acronym"><xsl:value-of select="root/conference/acronym" /></alt-title>
          </book-title-group>
          <contrib-group>
            <xsl:for-each select="root/chairs/element">
              <xsl:variable name="chair_id">bkseq-<xsl:number format="00001" value="seq_no" /></xsl:variable>
              <contrib contrib-type="editor" id="{$chair_id}">
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
          <publisher>
            <publisher-name><xsl:value-of select="root/publisher/name" /></publisher-name>
            <publisher-name specific-use="publisher-id db-only"><xsl:value-of select="root/publisher/id" /></publisher-name>
            <publisher-loc>
              <xsl:if test="root/publisher/address">
                <xsl:value-of select="root/publisher/address" />,
              </xsl:if>
              <xsl:if test="root/publisher/city">
                <xsl:value-of select="root/publisher/city" />,
              </xsl:if>
              <xsl:if test="root/publisher/province">
                <xsl:value-of select="root/publisher/province" />,
              </xsl:if>
              <xsl:value-of select="root/publisher/country" />
            </publisher-loc>
          </publisher>
          <permissions>
            <copyright-year><xsl:value-of select="root/publication/copyright/year" /></copyright-year>
            <copyright-holder><xsl:value-of select="root/publication/copyright/holder" /></copyright-holder>
          </permissions>
          <xsl:if test="root/publication/digital_edition/url != ''">
            <self-uri content-type="external" xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="{root/publication/digital_edition/url}">
              <xsl:value-of select="root/publication/digital_edition/description" />
            </self-uri>
          </xsl:if>
          <xsl:if test="root/publication/front_matter/uri != ''">
            <self-uri content-type="fm-pdf" xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="{root/publication/front_matter/uri}">
              <xsl:value-of select="root/publication/front_matter/description" />
            </self-uri>
          </xsl:if>
          <xsl:if test="root/publication/back_matter/uri != ''">
            <self-uri content-type="bm-pdf" xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="{root/publication/back_matter/uri}">
              <xsl:value-of select="root/publication/back_matter/description" />
            </self-uri>
          </xsl:if>
          <abstract>
            <p><xsl:value-of select="root/publication/abstract" /></p>
          </abstract>
          <conference>
            <conf-name>
              <ext-link ext-link-type="url" xlink:href="{root/conference/url}">
                <xsl:value-of select="root/conference/acronym" /></ext-link>:
                <xsl:value-of select="root/conference/description" />
              </conf-name>
              <conf-date iso-8601-date="">
                <day content-type="start-day"><xsl:value-of select="root/conference/start_date/day" /></day>
                <month content-type="start-month"><xsl:value-of select="root/conference/start_date/month" /></month>
                <year content-type="start-year"><xsl:value-of select="root/conference/start_date/year" /></year>
                <day content-type="end-day"><xsl:value-of select="root/conference/start_date/day" /></day>
                <month content-type="end-month"><xsl:value-of select="root/conference/start_date/month" /></month>
                <year content-type="end-year"><xsl:value-of select="root/conference/start_date/year" /></year>
              </conf-date>
              <conf-loc>
                <city><xsl:value-of select="root/conference/location/city" /></city>
                <state><xsl:value-of select="root/conference/location/province" /></state>
                <country><xsl:value-of select="root/conference/location/country" /></country>
              </conf-loc>
              <conf-acronym><xsl:value-of select="root/conference/acronym" /></conf-acronym>
              <xsl:for-each select="root/sponsors/element">
                <xsl:element name="conf-sponsor">
                  <xsl:attribute name="specific-use">sponsor</xsl:attribute>
                  <xsl:if test="id">
                    <xsl:attribute name="id"><xsl:value-of select="id" /></xsl:attribute>
                  </xsl:if>
                  <abbrev><xsl:value-of select="abbr" /></abbrev> <xsl:value-of select="name" />
                </xsl:element>
              </xsl:for-each>
            </conference>
            <counts><book-page-count count="{root/publication/pages}" /></counts>
          </book-meta>
          <front-matter>
            <toc>
              <xsl:for-each select="root/sessions/element">
                <toc-div>
                  <toc-title-group>
                    <label><xsl:value-of select="label" /></label>
                    <title><xsl:value-of select="title" /></title>
                  </toc-title-group>
                  <!-- <toc-entry>
                  <title>Session details: <xsl:value-of select="title" /></title>
                  <subtitle></subtitle>
                  <nav-pointer-group>
                  <nav-pointer>
                  <ext-link ext-link-type="doi">
                  <xsl:value-of select="/root/publication/doi" />.<xsl:value-of select="doi" />
                </ext-link>
              </nav-pointer>
            </nav-pointer-group>
          </toc-entry> -->
          <xsl:for-each select="articles/element">
            <toc-entry>
              <title><xsl:value-of select="title" /></title>
              <subtitle><xsl:value-of select="subtitle" /></subtitle>
              <nav-pointer-group>
                <nav-pointer>
                  <ext-link ext-link-type="doi">
                    <xsl:value-of select="/root/publication/doi" />.<xsl:value-of select="doi" />
                  </ext-link>
                </nav-pointer>
                <nav-pointer content-type="label" specific-use="pages"><xsl:value-of select="page_from" />-<xsl:value-of select="page_to" /></nav-pointer>
                <nav-pointer content-type="label" specific-use="article-no"><xsl:value-of select="number" /></nav-pointer>
              </nav-pointer-group>
            </toc-entry>
          </xsl:for-each>
        </toc-div>
      </xsl:for-each>
    </toc>
  </front-matter>
</book>
</xsl:template>
</xsl:stylesheet>
