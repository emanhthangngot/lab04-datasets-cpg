// MongoDB evidence queries for Lab04 metadata ingestion.
// Run in mongosh after Spark has consumed cpg.metadata.

db = db.getSiblingDB("cpg");

print("Total metadata documents:");
printjson(db.file_metadata.countDocuments());

print("Duplicate file_id documents:");
printjson(
  db.file_metadata
    .aggregate([
      { $group: { _id: "$file_id", count: { $sum: 1 } } },
      { $match: { count: { $gt: 1 } } },
    ])
    .toArray()
);

print("Recent replay candidates:");
printjson(db.file_metadata.find({}, { file_path: 1, content_hash: 1, run_id: 1 }).limit(5).toArray());
