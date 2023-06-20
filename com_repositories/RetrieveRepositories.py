import requests
import main


def getRepos(url, max_file_size, max_chunk_size):
    most_complex_repo = None
    highest_complexity = float('-inf')
    justification = ""
    username = url.split("/")
    username = username[-1]
    response = requests.get(f"https://api.github.com/users/{username}/repos")
    if response.status_code == 200:
        repos = response.json()
        repo_names = [r["name"] for r in repos]

        # repo_names = [r["name"] for r in repositories]

        for r in repo_names:
            print(f"Processing repository {r}")
            response = requests.get(f"https://api.github.com/repos/{username}/{r}/contents")
            if response.status_code == 200:
                contents = response.json()
                for file in contents:
                    file_name = file["name"]
                    file_url = file["download_url"]
                    file_size = file["size"]

                    if file_size <= max_file_size:
                        try:
                            response = requests.get(file_url)
                        except Exception as e:
                            print("Could not read file due to " + str(e))
                        if response.status_code == 200:
                            file_content = response.text

                            # Chunk the file content if it exceeds the maximum chunk size
                            if len(file_content) > max_chunk_size:
                                chunks = main.chunk_large_files(file_content, max_chunk_size)

                                for chunk in chunks:
                                    tech_complexity = main.evaluate_complexity(chunk)

                                    print("Chunk technical complexity {tech_complexity}")
                                    if tech_complexity > highest_complexity:
                                        highest_complexity = tech_complexity
                                        most_complex_repo = r
                                        justification = justification.generate_justification(chunk)
                            else:
                                tech_complexity = main.evaluate_complexity(file_content)
                                print(f"File Technical Complexity {tech_complexity}")
                                if tech_complexity > highest_complexity:
                                    highest_complexity = tech_complexity
                                    most_complex_repo = r
                                    justification = justification.generate_justification(file_content)
                        else:
                            print(f"failed to fetch content for {file_name}")
                    else:
                        print(f"skipping large file {file_name}")
            else:
                print(f"Failed to fetch contents for repository: {r}")

    else:
        print("unable to fetch user's repository")
    return highest_complexity, most_complex_repo, justification
