# Beach facts checked 16 Nov 2026 against the linked agency pages.
# A field is "unstated" when that page does not say. Do not fill gaps from memory.

REGIONS = {
    "gulf": {"name": "Gulf Coast", "blurb": "Sarasota, the islands north of it, Charlotte, Lee and Collier.",
             "intro": "Gulf beaches from Pasco to Collier, chosen by parking, dogs, and lifeguards. Sunset direction is a separate guide."},
    "atlantic": {"name": "Atlantic Coast", "blurb": "From Nassau and Duval down the east coast to Miami-Dade.",
                 "intro": "Atlantic pages face east. Surf, inlets and sunrise light are the usual story, and red tide can still arrive by current."},
    "panhandle": {"name": "Panhandle", "blurb": "Franklin, Bay, Walton, Okaloosa and Escambia state park beaches.",
                  "intro": "Panhandle pages are mostly Florida State Parks on the Gulf, plus Big Lagoon on the Intracoastal, which the park says is not a Gulf beach."},
    "keys": {"name": "Florida Keys", "blurb": "State park beaches from Key Largo to Key West.",
             "intro": "Keys pages use Florida State Parks. Some shores face the Atlantic, some face Florida Bay, and Bahia Honda has both."},
}

COUNTIES = {
    "sarasota": "Sarasota County", "manatee": "Manatee County", "pinellas": "Pinellas County",
    "hillsborough": "Hillsborough County", "pasco": "Pasco County", "charlotte": "Charlotte County",
    "lee": "Lee County", "collier": "Collier County", "walton": "Walton County", "okaloosa": "Okaloosa County",
    "escambia": "Escambia County", "bay": "Bay County", "franklin": "Franklin County", "st-johns": "St. Johns County",
    "indian-river": "Indian River County", "palm-beach": "Palm Beach County", "miami-dade": "Miami-Dade County",
    "duval": "Duval County", "broward": "Broward County", "st-lucie": "St. Lucie County", "monroe": "Monroe County",
    "nassau": "Nassau County",
}

def fsp(slug, label):
    return ("Florida State Parks: %s" % label, "https://www.floridastateparks.org/parks-and-trails/%s/experiences-amenities" % slug)

SRQ = ("Sarasota County: beach directory", "https://www.sarasotacountyparks.com/parks-and-facilities/discover-a-park/type-of-park/beaches")
SRQH = ("Sarasota County: beach and parking hours", "https://sarasotacountyfl.qscend.com/311/knowledgebase/article/1010")
SIESTA = ("Sarasota County: Siesta Beach", "https://www.sarasotacountyparks.com/parks-and-facilities/discover-a-park/destination-parks/siesta-beach")
PIN_FAQ = ("Pinellas County: parks and preserves questions", "https://pinellas.gov/parks-and-preserves-frequently-asked-questions/")
PIN_DOG = ("Pinellas County: dog parks", "https://pinellas.gov/dog-parks/")
PIN_LIFE = ("Pinellas County: seasonal lifeguard notice", "https://pinellas.gov/news/lifeguards-needed-for-2026-beach-season/")
MAN_LIFE = ("Manatee County: lifeguarded beaches", "https://www.mymanatee.org/services-and-amenities/service-listing/service-details/find-a-lifeguarded-beach")

FEE = "The experiences page does not list the day use entrance fee. Check the park fees page before you go."
NOFILL = "The page does not say what time the lot fills."
NOCHAIR = "The page we checked does not list a beach wheelchair."
NOMAT = "The page we checked does not list an access mat."
NOSHELL = "The page we checked does not describe shelling."
SRQ_DOG_QUIET = "The county directory does not mark this beach dog friendly. The Siesta Beach page allows only service animals on that beach. Confirm this beach on the county dog page before you bring a pet."
SRQ_PARK = "Sarasota County says its beach parking lots are open 6 a.m. to 10 p.m. unless a sign says otherwise, and that overnight parking is not allowed. This directory entry does not state a fee or a space count."
SRQ_GUARD_YES = "The county directory lists a lifeguard. The directory entry does not print the hours."
SRQ_GUARD_NO = "Lifeguard is not in the amenity list the county publishes for this beach. Treat the water as unguarded unless a sign on site says otherwise."
SRQ_REST_YES = "The county directory lists a restroom."
SRQ_REST_NO = "The county directory does not list a restroom."

BEACHES = []

def add(**k):
    k.setdefault("extra", [])
    k.setdefault("sunset", False)
    k.setdefault("kids", False)
    k.setdefault("free_access", False)
    k.setdefault("faqs", None)
    k.setdefault("snorkel", "no")
    k.setdefault("snorkel_note", "")
    BEACHES.append(k)

def srq(slug, name, short, place, rest, guard, dogs, dogs_note, parking, fills, angle, who, nearby, kids=False, extra=None, sources=None, shell_note=NOSHELL, shell="unstated"):
    add(slug=slug, name=name, short=short, region="gulf", county="sarasota", county_name="Sarasota County",
        place=place, manager="Sarasota County Parks", water="gulf", dogs=dogs, shell=shell, chair="unstated", mat="unstated",
        guard=guard, restroom="yes" if rest == "yes" else "unstated", kids=kids, sunset=False, parking=parking, fills=fills,
        dogs_note=dogs_note, shell_note=shell_note, chair_note=NOCHAIR, mat_note=NOMAT,
        guard_note=SRQ_GUARD_YES if guard == "yes" else SRQ_GUARD_NO,
        rest_note=SRQ_REST_YES if rest == "yes" else SRQ_REST_NO,
        angle=angle, who=who, sources=sources or [SRQ, SRQH], nearby=nearby, extra=extra or [])

# --- Sarasota, including Siesta Key ---
add(slug="siesta-beach", name="Siesta Beach", short="Siesta Beach", region="gulf", county="sarasota", county_name="Sarasota County",
    place="Siesta Key", manager="Sarasota County Parks", water="gulf", dogs="service", shell="unstated", chair="yes", mat="yes",
    guard="yes", restroom="yes", kids=True, sunset=False, free_access=True,
    parking="The Siesta Beach page says there are over 950 free spaces, including recreational vehicles, motorcycles and accessible spaces. The county hours page says that lot is open year round from 6 a.m. to 10 p.m. The same page says the Siesta Key Breeze trolley is free and runs 8 a.m. to 10 p.m. every day, with modified hours on some holidays.",
    fills="The county pages we checked do not say what time the lot fills. They do call this the most parking of any public beach in the county, and they call the beach a top tourist stop.",
    dogs_note="The Siesta Beach page says only service animals are allowed on Siesta Beach.",
    shell_note="The Siesta Beach page describes nearly 100 percent quartz crystal sand and says it does not get hot. It does not describe shelling.",
    chair_note="The Siesta Beach page says beach wheelchairs are free, year round, from the parking areas to the shore, and that they are signed out at the main pavilion concession. Users complete a liability form. The page tells you to ask about availability. We do not print the phone number here.",
    mat_note="The Sarasota County beaches page says an access mat at Siesta Beach extends 504 feet toward the Gulf.",
    guard_note="The Sarasota County beaches page says lifeguards are on duty 10 a.m. to 4:45 p.m., seven days a week, at six named beaches including Siesta Beach.",
    rest_note="The Siesta Beach page says there are plenty of restrooms and no dedicated changing rooms.",
    angle="Siesta Beach is the Sarasota County park with the large free lot, a published lifeguard window, a free beach wheelchair and a 504 foot access mat.",
    who="It suits a group that wants a staffed Gulf swim, a playground, food, and step free help, and that can use the free trolley if the lot is busy. It does not suit someone bringing a pet dog.",
    sources=[SIESTA, SRQ, SRQH], nearby=["turtle-beach", "siesta-access-12", "siesta-access-1"],
    published="2026-11-19",
    extra=["The county also lists a shaded playground, concessions, sand volleyball, pickleball and tennis. Alcohol is allowed for people of legal drinking age. Glass is prohibited. The page links out for red tide instead of describing current conditions."])

srq("turtle-beach", "Turtle Beach", "Turtle Beach", "Siesta Key", "yes", "unstated", "unstated", SRQ_DOG_QUIET, SRQ_PARK, NOFILL,
    "Turtle Beach is the staffed county park at the south end of Siesta Key, with a boat ramp, a fishing pier and a playground, and no lifeguard in the directory list.",
    "It suits a south island day with a boat or a picnic, if you do not need a lifeguard on the directory list. Pair it with Siesta Beach when you want a guarded swim.",
    ["siesta-beach", "palmer-point", "siesta-access-13"])

srq("turtle-campground", "Turtle Beach Campground", "Turtle Beach Campground", "Siesta Key", "yes", "unstated", "unstated", SRQ_DOG_QUIET,
    "The county directory titles this campground as having no beach parking. Beach parking is a different question from a campsite. Read the county campground rules before you treat a site as a day lot.",
    "The directory does not say when any nearby day lot fills.",
    "Turtle Beach Campground is the county campground on Siesta Key. The directory title says it has no beach parking.",
    "It suits someone who already has a campsite and wants to know the county does not offer this lot as beach parking. Day visitors should use Turtle Beach or Siesta Beach.",
    ["turtle-beach", "siesta-beach"])

srq("lido-beach", "Lido Beach", "Lido Beach", "Lido Key", "yes", "yes", "unstated", SRQ_DOG_QUIET, SRQ_PARK, NOFILL,
    "Lido Beach is the county beach on Lido Key with a lifeguard, a concession, a pool and restrooms on the directory list.",
    "It suits a guarded swim close to downtown Sarasota, including someone who wants a pool as well as the Gulf. Confirm the dog rule before you bring a pet.",
    ["north-lido", "south-lido", "siesta-beach"], kids=True,
    extra=["The directory also lists picnic shelters. It does not state a parking space count."])

srq("north-lido", "North Lido Beach", "North Lido Beach", "Lido Key", "unstated", "unstated", "unstated", SRQ_DOG_QUIET,
    "The county directory titles North Lido Beach as having no parking. The hours page does not add a lot for it.",
    "There is no lot on the directory title, so a fill time is not published.",
    "North Lido Beach is the county access titled as having no parking. The directory lists beach access, birding, picnicking, an unpaved trail and wildlife viewing.",
    "It suits a walk in from Lido Beach if you do not need a restroom or a lifeguard on the directory list.",
    ["lido-beach", "south-lido"])

srq("south-lido", "Ted Sperling Park at South Lido", "South Lido", "Lido Key", "yes", "unstated", "unstated", SRQ_DOG_QUIET, SRQ_PARK, NOFILL,
    "Ted Sperling Park at South Lido is the county park at the south end of Lido Key. The directory lists a playground, restrooms, picnicking and an unpaved trail, and it does not list swimming or a lifeguard.",
    "It suits a playground and a walk more than a guarded swim. Use Lido Beach if you want the lifeguard the directory lists there.",
    ["lido-beach", "north-lido"], kids=True)

srq("nokomis-beach", "Nokomis Beach", "Nokomis Beach", "Nokomis", "yes", "yes", "unstated", SRQ_DOG_QUIET, SRQ_PARK, NOFILL,
    "Nokomis Beach is a guarded county beach with a playground, a concession, a fishing pier, a boat ramp and sand volleyball on the directory list.",
    "It suits a family day on the south county Gulf shore when you want a lifeguard and a playground in one park.",
    ["north-jetty", "venice-beach", "manasota-beach"], kids=True)

srq("north-jetty", "North Jetty Park", "North Jetty", "Nokomis", "yes", "yes", "unstated", SRQ_DOG_QUIET, SRQ_PARK, NOFILL,
    "North Jetty Park is a guarded county beach at the south end of Casey Key, with a playground, a concession and a kayak launch on the directory list.",
    "It suits a jetty walk and a guarded swim. The directory does not describe the current or the fishing rules beyond listing fishing.",
    ["nokomis-beach", "venice-beach"], kids=True)

srq("venice-beach", "Venice Beach", "Venice Beach", "Venice", "yes", "yes", "unstated", SRQ_DOG_QUIET, SRQ_PARK, NOFILL,
    "Venice Beach is a guarded county beach with a concession, sand volleyball and restrooms. The directory does not mention shark teeth or shelling.",
    "It suits a guarded swim in Venice. If you came for shells, the county page we checked does not describe that, so do not treat this guide as a shell report.",
    ["north-brohard", "south-brohard", "caspersen-beach"], kids=True)

srq("manasota-beach", "Manasota Beach", "Manasota Beach", "Englewood", "yes", "yes", "unstated", SRQ_DOG_QUIET, SRQ_PARK, NOFILL,
    "Manasota Beach is a guarded county beach on Manasota Key with boat ramps for motorized and paddle craft, fishing and restrooms.",
    "It suits a guarded swim at the south end of the county, especially if you are also launching a boat.",
    ["blind-pass", "caspersen-beach"], kids=True)

add(slug="caspersen-beach", name="Caspersen Beach", short="Caspersen: Walk In, Lot Closed", region="gulf", county="sarasota",
    county_name="Sarasota County", place="Venice", manager="Sarasota County Parks", water="gulf",
    dogs="unstated", shell="unstated", chair="unstated", mat="unstated", guard="unstated", restroom="unstated",
    kids=False, sunset=False,
    parking="The facility page says the Harbor Drive access washed out during the 2024 storm season. Vehicle parking is closed. The park is open to people on foot and on bicycles. The county says to enter from South Brohard Park or from the Venetian Waterway Park Trail at the City of Venice Festival Grounds. It does not state a fee, because there is no vehicle lot open to charge.",
    fills="There is no vehicle lot open on the facility page, so a fill time for Caspersen itself does not apply. The page does not say when South Brohard fills.",
    dogs_note="The facility page amenity list does not mark Caspersen dog friendly, and it does not say pets are prohibited. Confirm the county dog page before you bring a pet.",
    shell_note="The facility page does not describe shelling or fossil teeth. This guide does not add either from a tourism writeup.",
    chair_note=NOCHAIR, mat_note=NOMAT,
    guard_note="Lifeguard is not in the amenity list on the facility page. Treat the water as unguarded unless a sign on site says otherwise.",
    rest_note="The facility page says the restrooms are closed until repairs, along with vehicle parking and the playground. Hours on that page are 6 a.m. to 10 p.m.",
    angle="Caspersen Beach is open on foot and by bicycle. The county says the vehicle lot, restrooms, and playground have been closed since the 2024 storm washout.",
    who="It suits a walk or a bike ride in from South Brohard when you do not need a restroom, a playground, or a lifeguard on the Caspersen list. It does not suit a car.",
    sources=[
        ("Sarasota County: Caspersen Beach Park", "https://www.sarasotacountyparks.com/Home/Components/FacilityDirectory/FacilityDirectory/603/6738"),
        SRQ, SRQH,
    ],
    nearby=["venice-beach", "service-club", "blind-pass", "south-brohard"],
    verified="2026-11-20", modified="2026-11-20",
    extra_html=[
        '<p>The practical change is the entrance, not a new amenity list. On 20 Nov 2026 the county facility page still listed beach access, bicycling, birding, a canoe or kayak launch, fishing, grills, outdoor fitness equipment, picnicking, swimming, an unpaved trail, and wildlife viewing. In the same paragraph it said the Harbor Drive access washed out during the 2024 storm season and that restrooms, vehicle parking, and the playground stay closed until repairs. Entry is from <a href="/beaches/south-brohard/">South Brohard Park</a> or the Venetian Waterway Park Trail at the City of Venice Festival Grounds. We do not print the street address or a phone number. Use the county link.</p>',
        '<p>South Brohard is the car access the county names. Its directory line still lists a restroom. Caspersen\'s own restroom is the one the facility page says is closed. <a href="/beaches/venice-beach/">Venice Beach</a> is the nearby listing that includes a lifeguard. <a href="/beaches/service-club/">Service Club Park</a> is the picnic and volleyball listing, also without a lifeguard in the directory. None of those pages is a promise about the water.</p>',
        '<p>People ask Caspersen about fossil teeth. The facility page we checked does not mention teeth or shells, so this page does not either. If a later county page adds that, the shelling guide is where it would belong. The <a href="/counties/sarasota/">Sarasota County</a> hub is the rest of the directory.</p>',
    ],
    reads={
        "mid": [
            ("/beaches/south-brohard/", "South Brohard Park", "The county says to enter Caspersen from here. The directory still lists a restroom."),
            ("/beaches/venice-beach/", "Venice Beach", "The nearby county beach whose directory lists a lifeguard."),
            ("/beaches/service-club/", "Service Club Park", "Picnic and volleyball in Venice, with no lifeguard in the list."),
        ],
        "end": [
            ("/counties/sarasota/", "Sarasota County beaches", "The rest of the county directory, including Siesta."),
            ("/beaches/siesta-beach/", "Siesta Beach", "The large free lot if the day depends on parking."),
            ("/guides/how-to-pick-a-florida-beach/", "How to pick a Florida beach", "A closed lot is the constraint. Start there."),
            ("/regions/gulf/", "Gulf Coast beaches", "The county map, not a sunset ranking."),
        ],
        "compare": '<p>Need a car and a restroom? Start at <a href="/beaches/south-brohard/">South Brohard</a>, which is the access the county names, and whose directory still lists a restroom. Need a lifeguard on the published list? <a href="/beaches/venice-beach/">Venice Beach</a> has one. Caspersen is the walk-in shore with the lot, the restrooms, and the playground closed.</p>',
    },
    faqs=[
        ("Can I park a car at Caspersen Beach?", "Not on the facility page checked 20 Nov 2026. Vehicle parking is closed. The county says to enter on foot or by bicycle from South Brohard Park or the Venetian Waterway Park Trail."),
        ("Are the Caspersen restrooms and playground open?", "The same page says restrooms, vehicle parking, and the playground are closed until repairs. Hours printed there are 6 a.m. to 10 p.m."),
        ("Is there a lifeguard at Caspersen Beach?", "Lifeguard is not in the amenity list. Treat the water as unguarded unless a sign on site says otherwise."),
        ("Does the county page mention shark teeth at Caspersen?", "No. The facility page does not mention fossil teeth or shelling. This guide does not add that from a tourism site."),
    ])

srq("blind-pass", "Blind Pass Beach", "Blind Pass Beach", "Englewood", "yes", "unstated", "unstated", SRQ_DOG_QUIET, SRQ_PARK, NOFILL,
    "Blind Pass Beach is a county park on Manasota Key with restrooms, swimming, fishing, a kayak launch and picnic shelters. A lifeguard is not in the list.",
    "It suits a picnic and a swim on Manasota Key when you can do without the lifeguard the county lists at Manasota Beach.",
    ["manasota-beach", "caspersen-beach"])

srq("palmer-point", "Palmer Point Beach", "Palmer Point", "Siesta Key", "unstated", "unstated", "unstated", SRQ_DOG_QUIET,
    "The county directory titles Palmer Point as having no parking and as watercraft access only.",
    "There is no car lot on the directory title.",
    "Palmer Point is the county beach at the south end of Siesta Key that the directory limits to watercraft access. It lists swimming, fishing, a kayak launch and an unpaved trail.",
    "It suits a kayak or boat landing, not a car day. Use Turtle Beach if you need a ramp you can drive to.",
    ["turtle-beach", "siesta-access-13"])

srq("service-club", "Service Club Park", "Service Club Park", "Venice", "yes", "unstated", "unstated", SRQ_DOG_QUIET, SRQ_PARK, NOFILL,
    "Service Club Park is a county beach in Venice with restrooms, sand volleyball, grills and picnic shelters. A lifeguard is not in the list.",
    "It suits a picnic and volleyball day in Venice when the guarded swim at Venice Beach is not the point.",
    ["venice-beach", "caspersen-beach"])

srq("maxine-barritt", "Maxine Barritt Park", "Maxine Barritt Park", "Venice", "yes", "unstated", "yes",
    "The county directory lists Maxine Barritt Park as dog friendly with a leash required. It does not describe an off leash area.",
    SRQ_PARK, NOFILL,
    "Maxine Barritt Park is one of two Sarasota County beach listings marked dog friendly with a leash required. It also lists swimming, fishing, restrooms and a paved trail.",
    "It suits a leashed dog and a swim in Venice. It is not the off leash dog beach. South county dog plans should still be confirmed on the county dog page.",
    ["venice-beach", "south-brohard", "siesta-access-1"])

srq("north-brohard", "North Brohard Park", "North Brohard Park", "Venice", "yes", "unstated", "unstated", SRQ_DOG_QUIET, SRQ_PARK, NOFILL,
    "North Brohard Park is a Venice beach listing with a fishing pier, a bait shop, a concession and restrooms. A lifeguard is not in the list.",
    "It suits a pier and a concession more than a guarded swim. Venice Beach is the nearby listing that includes a lifeguard.",
    ["venice-beach", "south-brohard"])

srq("south-brohard", "South Brohard Park", "South Brohard Park", "Venice", "yes", "unstated", "unstated", SRQ_DOG_QUIET, SRQ_PARK, NOFILL,
    "South Brohard Park is a short county listing: beach access, birding, fishing, a restroom, swimming and wildlife viewing. No lifeguard is listed.",
    "It suits a simple swim and a restroom in Venice. Read Maxine Barritt if you need the dog friendly listing.",
    ["north-brohard", "maxine-barritt"])

# Numbered Siesta Key accesses. Facts are the directory line plus the county hours page.
def acc(slug, name, short, parking, fills, dogs, dogs_note, guard, angle, who, nearby, kids=False):
    srq(slug, name, short, "Siesta Key", "unstated", guard, dogs, dogs_note, parking, fills, angle, who, nearby, kids=kids)

PED = "The county hours page says this access does not provide parking and is open to pedestrians at all hours. Dry sand at county beaches is otherwise listed as 6 a.m. to 10 p.m."
acc("siesta-access-1", "Siesta Key Beach Access 1", "Siesta Access 1",
    "The directory does not state a space count or a fee for Access 1. It is not on the hours page list of pedestrian only accesses.",
    NOFILL, "yes",
    "The county directory lists Siesta Key Beach Access 1 as dog friendly with a leash required. It does not describe an off leash area.",
    "unstated",
    "Siesta Key Beach Access 1 is the island access the county marks dog friendly with a leash required. The directory also lists swimming, birding and wildlife viewing, and it does not list a lifeguard or a restroom.",
    "It suits a leashed dog on Siesta Key. It does not replace Siesta Beach if you need a lifeguard, a restroom or a beach wheelchair.",
    ["siesta-beach", "maxine-barritt"])
acc("siesta-access-3", "Siesta Key Beach Access 3", "Siesta Access 3", PED, "There is no lot on the hours page, so a fill time does not apply.",
    "unstated", SRQ_DOG_QUIET, "unstated",
    "Siesta Key Beach Access 3 is one of the pedestrian accesses the county hours page says are open all hours and have no parking.",
    "It suits a walk to the water outside the main lot hours. It does not suit a car that needs a space.",
    ["siesta-access-10", "siesta-beach"])
acc("siesta-access-3b", "Siesta Key Beach Access 3B", "Siesta Access 3B", PED, "There is no lot on the hours page, so a fill time does not apply.",
    "unstated", SRQ_DOG_QUIET, "unstated",
    "Siesta Key Beach Access 3B is named with Access 3 on the county hours page as a 24 hour pedestrian access with no parking.",
    "It suits someone walking in. The hours page does not add a lifeguard, a restroom or a dog rule for 3B.",
    ["siesta-access-3", "siesta-beach"])
acc("siesta-access-4", "Siesta Key Beach Access 4", "Siesta Access 4",
    "The directory lists beach access, birding, swimming, an unpaved trail and wildlife viewing. It does not say the access is pedestrian only, and it does not state a space count or a fee.",
    NOFILL, "unstated", SRQ_DOG_QUIET, "unstated",
    "Siesta Key Beach Access 4 is a numbered neighborhood access. The directory gives it the short amenity list and does not list a lifeguard or a restroom.",
    "It suits a neighborhood swim if you already know where to leave the car. Use Siesta Beach for the published lot, lifeguards and wheelchair.",
    ["siesta-access-5", "siesta-beach"])
acc("siesta-access-5", "Siesta Key Beach Access 5", "Siesta Access 5",
    "The directory gives Access 5 the same short list as several numbered accesses: beach, birding, swimming, an unpaved trail and wildlife viewing. No space count and no fee are stated.",
    NOFILL, "unstated", SRQ_DOG_QUIET, "unstated",
    "Siesta Key Beach Access 5 is a separate county access with the short amenity list. It is not the main Siesta Beach pavilion.",
    "It suits a local swim. It does not publish the facilities the main beach page publishes.",
    ["siesta-access-4", "siesta-access-7"])
acc("siesta-access-7", "Siesta Key Beach Access 7", "Siesta Access 7",
    "The directory does not mark Access 7 as pedestrian only and does not state a fee or a space count.",
    NOFILL, "unstated", SRQ_DOG_QUIET, "unstated",
    "Siesta Key Beach Access 7 is another numbered access with beach, birding, swimming, an unpaved trail and wildlife viewing on the directory list.",
    "It suits the same kind of day as the other short accesses. The number is a different gate, not a different set of published facilities.",
    ["siesta-access-8", "siesta-beach"])
acc("siesta-access-8", "Siesta Key Beach Access 8", "Siesta Access 8",
    "The directory does not mark Access 8 as pedestrian only and does not state a fee or a space count.",
    NOFILL, "unstated", SRQ_DOG_QUIET, "unstated",
    "Siesta Key Beach Access 8 carries the short directory list and is not the lifeguard access.",
    "Use it as a neighborhood gate. Access 11 is the numbered access that lists a lifeguard.",
    ["siesta-access-7", "siesta-access-9"])
acc("siesta-access-9", "Siesta Key Beach Access 9", "Siesta Access 9",
    "The directory does not mark Access 9 as pedestrian only and does not state a fee or a space count.",
    NOFILL, "unstated", SRQ_DOG_QUIET, "unstated",
    "Siesta Key Beach Access 9 is the last of the short list accesses before the pedestrian only points the hours page names.",
    "It suits a simple swim. Do not expect the directory to add a restroom or a lifeguard.",
    ["siesta-access-8", "siesta-access-10"])
acc("siesta-access-10", "Siesta Key Beach Access 10", "Siesta Access 10", PED,
    "There is no lot on the directory title.", "unstated", SRQ_DOG_QUIET, "unstated",
    "Siesta Key Beach Access 10 is titled as pedestrian access with no parking. The hours page includes it among the all hour pedestrian accesses.",
    "It suits a walk to the beach. It does not suit a car.",
    ["siesta-access-11", "siesta-access-3"])
acc("siesta-access-11", "Siesta Key Beach Access 11", "Siesta Access 11", PED,
    "There is no lot on the directory title.", "unstated", SRQ_DOG_QUIET, "yes",
    "Siesta Key Beach Access 11 is a no parking pedestrian access that still lists a lifeguard. The hours page includes it among the all hour pedestrian accesses.",
    "It suits a guarded swim you can walk to. It does not solve parking. The directory does not print the lifeguard hours for this access.",
    ["siesta-beach", "siesta-access-10"], kids=True)
acc("siesta-access-12", "Siesta Key Beach Access 12", "Siesta Access 12",
    "The directory does not title Access 12 as pedestrian only, and it does not state a space count or a fee. The hours page does not put Access 12 on the all hour pedestrian list.",
    NOFILL, "unstated", SRQ_DOG_QUIET, "unstated",
    "Siesta Key Beach Access 12 is a numbered access the directory does not mark as no parking. The amenity list is still short: beach, birding, swimming, an unpaved trail and wildlife viewing.",
    "It is the south island access people use when the main lot is the problem, but the county page does not promise spaces. Confirm the lot on the directory before you rely on it.",
    ["siesta-beach", "turtle-beach"])
acc("siesta-access-13", "Siesta Key Beach Access 13", "Siesta Access 13", PED,
    "There is no lot on the directory title.", "unstated", SRQ_DOG_QUIET, "unstated",
    "Siesta Key Beach Access 13 is a no parking pedestrian access at the south end of the public list. The hours page includes it among the all hour pedestrian accesses.",
    "It suits a walk. Palmer Point, farther south, is the watercraft access.",
    ["palmer-point", "siesta-access-12"])

# --- Manatee, Pinellas, islands ---
add(slug="coquina-beach", name="Coquina Beach", short="Coquina Beach", region="gulf", county="manatee", county_name="Manatee County",
    place="Bradenton Beach", manager="Manatee County", water="gulf", dogs="no", shell="yes", chair="yes", mat="unstated",
    guard="yes", restroom="yes", kids=True, sunset=True,
    parking="The county location page lists parking. It does not state a price or a space count on the page we checked.",
    fills=NOFILL,
    dogs_note="The Coquina Beach page says pets are prohibited.",
    shell_note="The page invites a stroll for seashell treasures in its introduction. It does not publish a species list or a bag limit. FWC rules still apply, including the Manatee County limit on live shells.",
    chair_note="The amenity list includes beach wheelchairs. The page does not say where they are signed out.",
    mat_note=NOMAT,
    guard_note="The county lifeguard page names Coquina Beach as one of three beaches with lifeguards. The clock times printed on the Coquina location page are written as the Manatee Public Beach schedule. Confirm Coquina's hours on the county page.",
    rest_note="The amenity list includes restrooms.",
    angle="Coquina Beach is a Manatee County beach on Anna Maria with a lifeguard station, beach wheelchairs, a playground, and an introduction that talks about the sun setting over the water.",
    who="It suits a guarded Gulf sunset and a playground, without a dog. Confirm the lifeguard clock on the county page rather than borrowing the Manatee Public Beach hours.",
    sources=[("Manatee County: Coquina Beach", "https://www.mymanatee.org/connect/locations/location-details/coquina-beach"), MAN_LIFE],
    nearby=["manatee-public-beach", "cortez-beach", "egmont-key"])

import more_beaches  # noqa: E402  (registers the rest of the beaches)
