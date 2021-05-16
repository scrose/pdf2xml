#!/usr/bin/env python3x

import requests

"""
===========================================
DOI Metadata Document (DataCite)
===========================================
Generates DataCite DOI Metadata files for REST API

<?php
/*
Template Name: Datacite RESTful Processor
*/
header('Content-type: text/html; charset=UTF-8');
ini_set('display_errors', 'On');

  function postMetadata ($url, $postdata = false) //single custom cURL request.
  {
      $ch = curl_init();
      curl_setopt($ch, CURLOPT_HEADER, TRUE);
      curl_setopt($ch, CURLINFO_HEADER_OUT, true);
      curl_setopt( $ch, CURLOPT_HTTPHEADER, array('Content-Type: application/xml'));
      curl_setopt($ch, CURLOPT_VERBOSE, true);
      curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

      curl_setopt($ch, CURLOPT_URL, $url);

      if ($postdata)
      {
          curl_setopt($ch, CURLOPT_POST, true);
          curl_setopt($ch, CURLOPT_POSTFIELDS, $postdata);
      }

      // Optional Authentication:
      curl_setopt($ch, CURLOPT_HTTPAUTH, CURLAUTH_BASIC);
      curl_setopt($ch, CURLOPT_USERPWD, "CISTI.CHCCS:graphicsinterface");

      $response = curl_exec($ch);

      curl_close($ch);

      return $response;
  }

  // Mint DOIs
  function mintDOI($url, $postdata = false)
  {
      $ch = curl_init();
      $headers = array(
                  "Content-Type:text/plain;charset=UTF-8",
              );

      curl_setopt($ch, CURLOPT_VERBOSE, 1);
      curl_setopt($ch, CURLOPT_HEADER, TRUE);
      curl_setopt($ch, CURLINFO_HEADER_OUT, true);
      curl_setopt($ch, CURLOPT_HTTPHEADER, $headers );
      curl_setopt($ch, CURLOPT_URL, $url);
      curl_setopt($ch, CURLOPT_POST, true);
      curl_setopt($ch, CURLOPT_POSTFIELDS, $postdata);


      curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
      curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);

      // Optional Authentication:
      curl_setopt($ch, CURLOPT_HTTPAUTH, CURLAUTH_BASIC);
      curl_setopt($ch, CURLOPT_USERPWD, "CISTI.CHCCS:graphicsinterface");


      curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);

      $ch_response = curl_exec($ch);

      // print_r(curl_getinfo($ch));

      $header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
      $header = substr($response, 0, $header_size);
      $body = substr($response, $header_size);
      echo $body;

        if ($ch_response === false) {
          $info = curl_getinfo($ch);
          curl_close($ch);
          die('error occured during curl exec. Additional info: ' . var_export($info));
        }
        curl_close($ch);
        return $ch_response;

  }

  function getDOI($url, $doi = false)
  {
      $ch = curl_init();
      $headers = array(
                  "Content-Type:text/plain;charset=UTF-8",
              );

      curl_setopt($ch, CURLOPT_HEADER, TRUE);
      curl_setopt($ch, CURLINFO_HEADER_OUT, true);
      curl_setopt($ch, CURLOPT_HTTPHEADER, $headers );
      curl_setopt($ch, CURLOPT_URL, $url.'/'.$doi);

      curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
      curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);

      // Optional Authentication:
      curl_setopt($ch, CURLOPT_HTTPAUTH, CURLAUTH_BASIC);
      curl_setopt($ch, CURLOPT_USERPWD, "CISTI.CHCCS:graphicsinterface");

      curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);

      $ch_response = curl_exec($ch);

      //print_r(curl_getinfo($ch));

        if ($ch_response === false) {
          $info = curl_getinfo($ch);
          curl_close($ch);
          die('error occured during curl exec. Additional info: ' . var_export($info));
        }
        curl_close($ch);
        return $ch_response;

  }

// ==================================
// Retrieve Proceedings

// Get the selected proceedings
$proceedings = get_field('selected_proceedings');

// Get the XML directory path
$xml_dir = 'http://graphicsinterface.org/wp-content/XML/'.get_field('conference_year').'/';

foreach ($proceedings as $key => $proceeding_id) {
  $conference_year = get_field('conference_year',$proceeding_id);
  $articles = get_attached_media( 'application/pdf', $proceeding_id);

  foreach ($articles as $key => $article) {
    $article_no = get_field('article_number', $article->ID);
    if ($article_no!=0) {
      $doi = '10.20380/GI'.$conference_year.'.'.sprintf('%02d', $article_no);
      $landing_pg = get_permalink($article->ID);
      // $xml_url = $xml_dir.'CMCCC'.get_field('conference_year',$proceeding_id).'-'.sprintf('%02d', $article_no).'.xml';
      $xml_url = $xml_dir.'GI'.get_field('conference_year',$proceeding_id).'-'.sprintf('%02d', $article_no).'.xml';

      // (STEP 1) Post XML metadata
      $metadata = file_get_contents($xml_url);
      $resp1 = postMetadata('https://mds.datacite.org/metadata', $metadata);

      echo 'XML URL: '.$xml_url.'</br>';
      echo '<b>Metadata RESPONSE:</b> '.$resp1.'</br><br />';

      // (STEP 2) Mint DOI
      $postdata = 'doi='.$doi.PHP_EOL.'url='.$landing_pg;
      $resp2 = mintDOI('https://mds.datacite.org/doi', $postdata );

      echo 'DOI: '.$doi.'</br>';
      echo 'URL: '.$landing_pg.'</br>';
      echo '<b>DOI RESPONSE:</b> '.$resp2.'<br /><hr />';

    }
  }
}

?>


<?php
/*
Template Name: DataCite XML Metadata
*/
ini_set('display_errors', 'On'); // DEBUG

?>

<?php get_header(); ?>
<div id="primary" class="content-area">
  <main id="main" class="site-main" role="main">

<?php
/**
 * The default template for displaying content
 *
 * Used for both single and index/archive/search.
 *
 * @package WordPress
 * @subpackage Twenty_Fifteen
 * @since Twenty Fifteen 1.0
 */

?>

<article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
	<header class="entry-header">
		<div class="sidebar-right"></div>
	</header><!-- .entry-header -->

	<div class="entry-content">



      <!-- Start XML -->
<?php
// Retrieve Proceedings Data
$proceedings_arr = array();
// Get the selected proceedings
$proceedings_arr[] = get_post(get_field('selected_proceedings')[0]);

foreach ($proceedings_arr as $key => $proceedings) {

  $proceedings_id = $proceedings->ID;
  $proceedings_year = get_field('conference_year', $proceedings_id);
  $proceedings_publisher = get_field('publisher', $proceedings_id);
  $proceedings_chairs = get_field('program_chairs', $proceedings_id);

  $proceedings_issn = get_field('issn', $proceedings_id);
  $proceedings_isbn = get_field('isbn', $proceedings_id);
  $proceedings_acm_doi = get_field('acm_doi', $proceedings_id);
  $proceedings_pagecount = get_field('pages', $proceedings_id);

  $articles = get_attached_media( 'application/pdf', $proceedings_id);

  foreach ($articles as $key => $article) {

    $article_id = $article->ID;
    $article_title = htmlspecialchars($article->post_title);
    $article_creators = get_field('creators', $article_id);
    $article_no = intval(get_field('article_number',$article_id));
    $article_acm_doi = get_field('acm_doi',$article_id);
    $article_filesize = size_format(filesize(get_attached_file($article_id)),2); 	// Get file size
    $article_abstract = get_field('abstract',$article_id);
    $article_series = get_field('subtitle', $article->post_parent).', '.get_field('location', $article->post_parent).', Canada, '.get_field('date', $article->post_parent).', '.get_field('page_range', $article_id);
    $article_keywords = get_field('keywords',$article_id);
    $article_pages = get_field('page_range', $article_id);
    $article_pagecount = get_field('page_count', $article_id);
    $article_doi = substr(get_field('doi',$article_id), strpos(get_field('doi',$article_id), "/") + 1);
    //$article_pagecount_arr = explode ("-",$article_pages);

    ?>
    <code>
    <pre>


    ---BREAK---

    </pre>
    </code>
    <?php

  }

?>
<?php   } ?>
  </div><!-- .entry-content -->

</article><!-- #post-## -->

</main><!-- .site-main -->
</div><!-- .content-area -->

<?php get_footer(); ?>

"""

def main():

    datacite_file = '/Users/boutrous/Workspace/Metadata/GI/2020/build/datacite/gi2020-01.xml'
    output_dir = '/Users/boutrous/Workspace/Metadata/GI/2020/build/datacite'
    with open(datacite_file) as fp:
       datacite_xml = fp.read()
    fp.close()

    url = "https://api.test.datacite.org/dois/id"

    headers = {"content-type": "application/vnd.api+json"}

    response = requests.request("PUT", url, headers=headers)

    print(response.text)


# Encapsulate in main()
if __name__ == "__main__":
    main()
    
    
# -- end of DataCite class --   