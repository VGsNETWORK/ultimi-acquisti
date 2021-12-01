#!/usr/bin/env python3

USER_INFO_NATIVE_QUERY = [
    # join with user collection
    {
        "$lookup": {
            "from": "subscriber",
            "localField": "user_id",
            "foreignField": "user_id",
            "as": "subscriber",
        }
    },
    {
        "$lookup": {
            "from": "user",
            "localField": "user_id",
            "foreignField": "user_id",
            "as": "user",
        }
    },
    # join with wishlist_element collection
    {
        "$lookup": {
            "from": "wishlist_element",
            "localField": "user_id",
            "foreignField": "user_id",
            "as": "wishlist_elements",
        }
    },
    # join with wishlist collection
    {
        "$lookup": {
            "from": "wishlist",
            "localField": "user_id",
            "foreignField": "user_id",
            "as": "wishlists",
        }
    },
    # - group elements by: user_id
    # - create an array with all the tracked links
    # - pass the elements of the user
    # - pass the wishlists of the user
    # - pass the user information
    {
        "$group": {
            "_id": "$user_id",
            "tracked_links": {"$push": "$subscriber.product_code"},
            "wishlist_elements": {"$first": "$wishlist_elements"},
            "wishlists": {"$first": "$wishlists"},
            "user": {"$first": "$user"},
        }
    },
    {
        # return the values
        "$project": {
            # do not return the _id
            "_id": 0,
            # return user_id
            "user_id": "$_id",
            # return the number of tracked_links
            "tracked_links": {"$size": {"$arrayElemAt": ["$tracked_links", 0]}},
            # return the number of wishlist_elements
            "wishlist_elements": {"$size": "$wishlist_elements"},
            # return the number of wishlists
            "wishlists": {"$size": "$wishlists"},
            # since the links is a list of lists you have to reduce it and then count it
            "links": {
                "$size": {
                    "$reduce": {
                        "input": "$wishlist_elements.links",
                        "initialValue": [],
                        "in": {"$concatArrays": ["$$this", "$$value"]},
                    }
                }
            },
            # since the photos is a list of lists you have to reduce it and then count it
            "photos": {
                "$size": {
                    "$reduce": {
                        "input": "$wishlist_elements.photos",
                        "initialValue": [],
                        "in": {"$concatArrays": ["$$this", "$$value"]},
                    }
                }
            },
            # return user_information
            "first_name": {"$arrayElemAt": ["$user.first_name", 0]},
            "last_name": {"$arrayElemAt": ["$user.last_name", 0]},
            "username": {"$arrayElemAt": ["$user.username", 0]},
        }
    },
    {"$sort": {"first_name": 1}},
]

ALL_USER_INFO_NATIVE_QUERY = [
    {"$match": {"user_id": 1121055937}},
    {
        "$lookup": {
            "from": "user",
            "localField": "user_id",
            "foreignField": "user_id",
            "as": "user",
        }
    },
    {
        "$lookup": {
            "from": "wishlist",
            "localField": "user_id",
            "foreignField": "user_id",
            "as": "wishlists",
        }
    },
    {
        "$lookup": {
            "from": "wishlist_element",
            "localField": "user_id",
            "foreignField": "user_id",
            "as": "wishlist_elements",
        }
    },
    {
        "$lookup": {
            "from": "subscriber",
            "localField": "user_id",
            "foreignField": "user_id",
            "as": "subscriber",
        }
    },
    {"$skip": 0},
    {"$limit": 1},
    {
        "$group": {
            "_id": "$user_id",
            "tracked_links": {"$push": "$subscriber.product_code"},
            "wishlist_elements": {"$first": "$wishlist_elements"},
            "wishlists": {"$first": "$wishlists"},
            "user": {"$first": "$user"},
        }
    },
    {
        "$project": {
            "_id": 0,
            "user_id": "$_id",
            "tracked_links": {"$size": {"$arrayElemAt": ["$tracked_links", 0]}},
            "wishlist_elements": {"$size": "$wishlist_elements"},
            "links": {
                "$size": {
                    "$reduce": {
                        "input": "$wishlist_elements.links",
                        "initialValue": [],
                        "in": {"$concatArrays": ["$$this", "$$value"]},
                    }
                }
            },
            "photos": {
                "$size": {
                    "$reduce": {
                        "input": "$wishlist_elements.photos",
                        "initialValue": [],
                        "in": {"$concatArrays": ["$$this", "$$value"]},
                    }
                }
            },
            "wishlists": {"$size": "$wishlists"},
            "linkedin": "$linkedin",
            "first_name": {"$arrayElemAt": ["$user.first_name", 0]},
            "last_name": {"$arrayElemAt": ["$user.last_name", 0]},
            "username": {"$arrayElemAt": ["$user.username", 0]},
        }
    },
]


def build_all_user_info_query(user_id: int):
    query = ALL_USER_INFO_NATIVE_QUERY.copy()
    query[0]["$match"]["user_id"] = user_id
    return query