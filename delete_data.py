from neo4j import GraphDatabase

# Connection
URI = "neo4j://127.0.0.1:7687"
AUTH = ("neo4j", "auxothon25")

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()

    # --- CLEAR ENTIRE DATABASE ---
    clear_query = "MATCH (n) DETACH DELETE n"
    _, summary, _ = driver.execute_query(clear_query, database_="neo4j")
    print(f"Deleted all nodes. Nodes deleted: {summary.counters.nodes_deleted}")

    # --- OPTIONAL: Check database is empty ---
    check_query = "MATCH (n) RETURN COUNT(n) AS total_nodes"
    records, summary, keys = driver.execute_query(check_query, database_="neo4j")
    for record in records:
        print(f"Total nodes remaining: {record['total_nodes']}")
