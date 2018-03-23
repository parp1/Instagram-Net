//Javascript query:
//Go to https://www.instagram.com/explore/tags/tag/ where tag is replaced with whatever hashtag you want to scrape
//Scroll down and click "Load more" once.
//Insert below script into console and run.
//Set __reactEventHandlers$ --- for the current session. TODO


var numberOfPicturesToScrape = 5000; //Enter number of images you want to scrape
var links = [];
var numSame = 0; //Tracker for stopping when can't load anymore images
var lastSeenLength = document.getElementsByClassName("_mck9w _gvoze _f2mse").length;

function downloadObjectAsJson(exportObj, exportName)
{
    var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportObj));
    var downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href",     dataStr);
    downloadAnchorNode.setAttribute("download", exportName + ".json");
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  }

var intervalID = window.setInterval(function() {

    if(numSame < 10 && document.getElementsByClassName("_mck9w _gvoze _f2mse").length < numberOfPicturesToScrape)
    {
        if (document.getElementsByClassName("_mck9w _gvoze _f2mse").length == lastSeenLength)
        {
            numSame++;
        }
        else
        {
            numSame = 0;
            lastSeenLength = document.getElementsByClassName("_mck9w _gvoze _f2mse").length;
        }

        window.scrollTo(0,document.body.scrollHeight);
        console.log("Scrolled to bottom to load more pictures.")

        setTimeout(function() { 
        	window.scrollTo(0,0);
    		console.log("Scrolled to top")
    	}, 250);
    }
    else
    {
        clearInterval(intervalID);
        alert("Finished!")

        if (confirm("Export data"))
        {
            var imgs = document.getElementsByClassName("_mck9w _gvoze _f2mse")
            var numImages = document.getElementsByClassName("_mck9w _gvoze _f2mse").length

            for (i = 0; i < numImages; i++)
            {
            	let ref = imgs[i].__reactEventHandlers$7zh3rwxr2zk //This needs to be set per session

                if (ref !== undefined)
                {
                	//let startIndex = imageDivHTML.indexOf("src=");
            		//let src = imageDivHTML.slice(startIndex + 5, -44);
                	links.push(ref.children.props.href);
                }
            }

            downloadObjectAsJson(links, "links");
        }
    }


}, 500);