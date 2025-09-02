from local_connector import LocalProposalConnector


def main():
    connector = LocalProposalConnector("./Auxo Proposals")

    # List all clients
    clients = connector.list_clients()
    print("Clients found:")
    for c in clients:
        print(" -", c)
    
    
   



if __name__ == "__main__":
    main()
