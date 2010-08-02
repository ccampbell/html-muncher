import urllib, httplib, re

class Tidier(object):
    url = "codebeautifier.com:80"
    @staticmethod
    def run(css):
        params = {"css_text" : css, 
                  "url" : "", 
                  "template" : 3, 
                  "custom" : "", 
                  "merge_selectors" : 2, 
                  "optimise_shorthands" : 1,
                  "compress_c" : "on",
                  "compress_fw" : "on",
                  "case_properties" : 1,
                  "rbs" : "on",
                  "css_level" : "CSS2.1",
                  "file_output" : "file_output"}
        
        encoded_params = urllib.urlencode(params)
        try:
            print "requesting minified css from codebeautifier"
            headers = {"Content-type" : "application/x-www-form-urlencoded", "Accept" : "text/plain"}
            conn = httplib.HTTPConnection(Tidier.url)
            conn.request("POST", "", encoded_params, headers)
            response = conn.getresponse()

            print "parsing response"

            html = response.read()
            match = re.search(r'<a href=\"(.*)\" ?>Download</a>', html)
        
            print "requesting new css file"
            conn = httplib.HTTPConnection(Tidier.url)
            conn.request("GET", "/" + match.group(1))
            response = conn.getresponse()
            print "saving new css file"
        except:
            print "error getting tidied up css from codebeautifier.com"
            return css

        return response.read()
