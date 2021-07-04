<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<xsl:output method="xml" />

	<xsl:variable name="admin_uid"><![CDATA[graphicsint]]></xsl:variable>
	<xsl:variable name="admin_email"><![CDATA[grand@gnwc.ca]]></xsl:variable>
	<xsl:variable name="admin_display_name"><![CDATA[Admin]]></xsl:variable>
	<xsl:variable name="admin_first_name"><![CDATA[Admin]]></xsl:variable>
	<xsl:variable name="admin_last_name"><![CDATA[]]></xsl:variable>

	<xsl:variable name="datestamp">
		<!-- FORMAT: YYYY-MM-DD HH:MM:SS -->
		<!-- <xsl:value-of select="format-dateTime(current-dateTime(),'[Y0001]-[M01]-[D01] [H01]:[m01]:[s]')"/> -->
	</xsl:variable>

	<xsl:variable name="post_type"><![CDATA[proceedings]]></xsl:variable>

	<xsl:template match="/">

		<rss version="2.0"
			xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/"
			xmlns:content="http://purl.org/rss/1.0/modules/content/"
			xmlns:wfw="http://wellformedweb.org/CommentAPI/"
			xmlns:dc="http://purl.org/dc/elements/1.1/"
			xmlns:wp="http://wordpress.org/export/1.2/"
			>

			<channel>
				<title>Graphics Interface</title>
				<link>https://graphicsinterface.org</link>
				<description>Conference on Graphics, Visualization &#38; HCI</description>
				<pubDate>
					<xsl:value-of  select="/root/timestamp"/>
				</pubDate>
				<language>en-CA</language>
				<wp:wxr_version>1.2</wp:wxr_version>
				<wp:base_site_url>https://graphicsinterface.org</wp:base_site_url>
				<wp:base_blog_url>https://graphicsinterface.org</wp:base_blog_url>

				<wp:author>
					<wp:author_id>1</wp:author_id>
					<wp:author_login>
						<xsl:copy-of select="$admin_uid" />
					</wp:author_login>
					<wp:author_email>
						<xsl:copy-of select="$admin_email" />
					</wp:author_email>
					<wp:author_display_name>
						<xsl:copy-of select="$admin_display_name" />
					</wp:author_display_name>
					<wp:author_first_name>
						<xsl:copy-of select="$admin_first_name" />
					</wp:author_first_name>
					<wp:author_last_name>
						<xsl:copy-of select="$admin_last_name" />
					</wp:author_last_name>
				</wp:author>


				<generator>https://wordpress.org/?v=5.4.1</generator>

				<xsl:for-each select="root/sessions/element">
					<xsl:variable name="section_title"><xsl:value-of select="title" /></xsl:variable>
					<xsl:for-each select="articles/element">

						<xsl:variable name="url">https://graphicsinterface.org/wp-content/uploads/<xsl:value-of select="wp_post_name" />.pdf</xsl:variable>
						<xsl:variable name="file"><xsl:value-of select="wp_post_name" />.pdf</xsl:variable>

						<item>
							<title><xsl:value-of select="title" /></title>
							<link><xsl:value-of select="url" /></link>
							<pubDate><xsl:value-of select="/root/timestamp" /></pubDate>
							<dc:creator><xsl:copy-of select="$admin_uid" /></dc:creator>
							<guid isPermaLink="false"><xsl:copy-of select="$url" /></guid>
							<description></description>
							<content:encoded><![CDATA[]]></content:encoded>
							<excerpt:encoded><![CDATA[]]></excerpt:encoded>
							<wp:post_id><xsl:value-of select="wp_post_id" /></wp:post_id>
							<wp:post_date><xsl:value-of select="post_date" /></wp:post_date>
							<wp:post_date_gmt><xsl:value-of select="post_date" /></wp:post_date_gmt>
							<wp:comment_status><![CDATA[closed]]></wp:comment_status>
							<wp:ping_status><![CDATA[closed]]></wp:ping_status>
							<wp:post_name><xsl:value-of select="wp_post_name" /></wp:post_name>
							<wp:status><![CDATA[private]]></wp:status>
							<wp:post_parent><xsl:value-of select="/root/wp_post_parent" /></wp:post_parent>
							<wp:menu_order>0</wp:menu_order>
							<wp:post_type><![CDATA[attachment]]></wp:post_type>
							<wp:post_password><![CDATA[]]></wp:post_password>
							<wp:is_sticky>0</wp:is_sticky>
							<wp:attachment_url><xsl:copy-of select="$url" /></wp:attachment_url>

							<category domain="post_tag" nicename="2020s"><![CDATA[2020s]]></category>
							<category domain="attachment_category" nicename="papers"><![CDATA[Conference Papers]]></category>
							<category domain="category" nicename="conference_proceedings"><![CDATA[Conference Proceedings]]></category>
							<category domain="post_tag" nicename="gi-proceedings"><![CDATA[Graphics Interface]]></category>
							<category domain="category" nicename="papers"><![CDATA[Papers]]></category>


							<wp:postmeta>
								<wp:meta_key><![CDATA[_wp_attached_file]]></wp:meta_key>
								<wp:meta_value><xsl:copy-of select="$url" /></wp:meta_value>
							</wp:postmeta>

							<wp:postmeta>
								<wp:meta_key><![CDATA[section_title]]></wp:meta_key>
								<wp:meta_value><xsl:copy-of select="$section_title" /></wp:meta_value>
							</wp:postmeta>
							<wp:postmeta>
								<wp:meta_key><![CDATA[_section_title]]></wp:meta_key>
								<wp:meta_value><![CDATA[field_5787252131e87]]></wp:meta_value>
							</wp:postmeta>

							<!-- article number -->
							<wp:postmeta>
								<wp:meta_key><![CDATA[article_number]]></wp:meta_key>
								<wp:meta_value><xsl:value-of select="number" /></wp:meta_value>
							</wp:postmeta>
							<wp:postmeta>
								<wp:meta_key><![CDATA[_article_number]]></wp:meta_key>
								<wp:meta_value><![CDATA[field_55144ebb2e3e3]]></wp:meta_value>
							</wp:postmeta>

							<!-- doi -->
							<wp:postmeta>
								<wp:meta_key><![CDATA[doi]]></wp:meta_key>
								<wp:meta_value><xsl:value-of select="doi" /></wp:meta_value>
							</wp:postmeta>
							<wp:postmeta>
								<wp:meta_key><![CDATA[_doi]]></wp:meta_key>
								<wp:meta_value><![CDATA[field_577f1d7b406ff]]></wp:meta_value>
							</wp:postmeta>

							<!-- abstract -->
							<wp:postmeta>
								<wp:meta_key><![CDATA[abstract]]></wp:meta_key>
								<wp:meta_value><xsl:value-of select="abstract" /></wp:meta_value>
								</wp:postmeta>
								<wp:postmeta>
									<wp:meta_key><![CDATA[_abstract]]></wp:meta_key>
									<wp:meta_value><![CDATA[field_55132c54a3a17]]></wp:meta_value>
								</wp:postmeta>

								<!-- keywords -->
								<wp:postmeta>
									<wp:meta_key><![CDATA[keywords]]></wp:meta_key>
									<wp:meta_value>
										<xsl:variable name="total_keywords">
											<xsl:value-of select="count(keywords/element)" />
										</xsl:variable>
										<xsl:for-each select="keywords/element">
											<xsl:value-of select="text()" />
											<xsl:if test="$total_keywords - position() > 0">, </xsl:if>
										</xsl:for-each>
									</wp:meta_value>
								</wp:postmeta>
								<wp:postmeta>
									<wp:meta_key><![CDATA[_keywords]]></wp:meta_key>
									<wp:meta_value><![CDATA[field_57872cb6a05cf]]></wp:meta_value>
								</wp:postmeta>

								<!-- creators -->
								<xsl:for-each select="authors/element">
									<wp:postmeta>
										<wp:meta_key>creators_<xsl:value-of select="position()" />_first_name</wp:meta_key>
										<wp:meta_value><xsl:value-of select="first_name" /></wp:meta_value>
									</wp:postmeta>
									<wp:postmeta>
										<wp:meta_key>_creators_<xsl:value-of select="position()" />_first_name</wp:meta_key>
										<wp:meta_value><![CDATA[field_577f1d0ead150]]></wp:meta_value>
									</wp:postmeta>
									<wp:postmeta>
										<wp:meta_key>creators_<xsl:value-of select="position()" />_last_name</wp:meta_key>
										<wp:meta_value><xsl:value-of select="last_name" /></wp:meta_value>
									</wp:postmeta>
									<wp:postmeta>
										<wp:meta_key>_creators_<xsl:value-of select="position()" />_last_name</wp:meta_key>
										<wp:meta_value><![CDATA[field_5787194d6daad]]></wp:meta_value>
									</wp:postmeta>
									<wp:postmeta>
										<wp:meta_key>creators_<xsl:value-of select="position()" />__affiliation</wp:meta_key>
										<wp:meta_value><![CDATA[]]></wp:meta_value>
									</wp:postmeta>
									<wp:postmeta>
										<wp:meta_key>_creators_<xsl:value-of select="position()" />__affiliation</wp:meta_key>
										<wp:meta_value><![CDATA[field_57a2f08447082]]></wp:meta_value>
									</wp:postmeta>
								</xsl:for-each>

								<!-- creators count -->
								<wp:postmeta>
									<wp:meta_key><![CDATA[creators]]></wp:meta_key>
									<wp:meta_value><xsl:value-of select="count(authors/element)" /></wp:meta_value>
								</wp:postmeta>
								<wp:postmeta>
									<wp:meta_key><![CDATA[_creators]]></wp:meta_key>
									<wp:meta_value><![CDATA[field_577f1ce2ad14f]]></wp:meta_value>
								</wp:postmeta>

								<!-- bibtex -->
								<wp:postmeta>
									<wp:meta_key><![CDATA[bibtex_data]]></wp:meta_key>
									<wp:meta_value><![CDATA[]]></wp:meta_value>
								</wp:postmeta>
								<wp:postmeta>
									<wp:meta_key><![CDATA[_bibtex_data]]></wp:meta_key>
									<wp:meta_value><![CDATA[field_5512f71773ee6]]></wp:meta_value>
								</wp:postmeta>

								<!-- page range -->
								<wp:postmeta>
									<wp:meta_key><![CDATA[page_range]]></wp:meta_key>
									<wp:meta_value><xsl:value-of select="page_from" /> - <xsl:value-of select="page_to" /></wp:meta_value>
								</wp:postmeta>
								<wp:postmeta>
									<wp:meta_key><![CDATA[_page_range]]></wp:meta_key>
									<wp:meta_value><![CDATA[field_577f22358b9a1]]></wp:meta_value>
								</wp:postmeta>

								<!-- page count -->
								<wp:postmeta>
									<wp:meta_key><![CDATA[page_count]]></wp:meta_key>
									<wp:meta_value><xsl:value-of select="pages" /></wp:meta_value>
								</wp:postmeta>
								<wp:postmeta>
									<wp:meta_key><![CDATA[_page_count]]></wp:meta_key>
									<wp:meta_value><![CDATA[field_579ad590d0976]]></wp:meta_value>
								</wp:postmeta>


						</item>
					</xsl:for-each>
				</xsl:for-each>
			</channel>
		</rss>
	</xsl:template>

</xsl:stylesheet>
