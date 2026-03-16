

class TestWinesEndpoint:
    def test_list_wines_default(self, client, auth_headers):
        response = client.get("/wines", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "wines" in data
        assert "total" in data
        assert data["total"] == 5

    def test_list_wines_with_pagination(self, client, auth_headers):
        response = client.get("/wines?page=1&limit=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["wines"]) == 2
        assert data["page"] == 1
        assert data["limit"] == 2

    def test_list_wines_filter_by_region(self, client, auth_headers):
        response = client.get("/wines?region=Napa", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert "Napa Valley" in data["wines"][0]["region"]

    def test_list_wines_filter_by_variety(self, client, auth_headers):
        response = client.get("/wines?variety=Red", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3

    def test_list_wines_filter_by_rating(self, client, auth_headers):
        response = client.get("/wines?min_rating=90", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        for wine in data["wines"]:
            assert wine["rating"] >= 90

    def test_list_wines_without_auth(self, client):
        response = client.get("/wines")
        assert response.status_code == 403


class TestWineById:
    def test_get_wine_by_id(self, client, auth_headers):
        response = client.get("/wines/0", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 0
        assert data["name"] == "Test Red Wine 2020"

    def test_get_wine_by_id_not_found(self, client, auth_headers):
        response = client.get("/wines/999", headers=auth_headers)
        assert response.status_code == 404


class TestSearch:
    def test_search_wines(self, client, auth_headers):
        response = client.get("/wines/search?q=cherry", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert "cherry" in data["wines"][0]["notes"].lower()

    def test_search_no_results(self, client, auth_headers):
        response = client.get("/wines/search?q=nonexistent", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["wines"] == []


class TestTopRated:
    def test_top_rated_default(self, client, auth_headers):
        response = client.get("/wines/top-rated", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["wines"][0]["rating"] == 95.0
        assert data["wines"][-1]["rating"] <= data["wines"][0]["rating"]

    def test_top_rated_with_limit(self, client, auth_headers):
        response = client.get("/wines/top-rated?limit=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["wines"]) == 2


class TestStats:
    def test_wine_stats(self, client, auth_headers):
        response = client.get("/wines/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_wines"] == 5
        assert "avg_rating" in data
        assert "rating_distribution" in data


class TestRegions:
    def test_list_regions(self, client, auth_headers):
        response = client.get("/regions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "regions" in data
        assert "Napa Valley" in data["regions"]

    def test_wines_by_region(self, client, auth_headers):
        response = client.get("/regions/Napa/wines", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1


class TestVarieties:
    def test_list_varieties(self, client, auth_headers):
        response = client.get("/varieties", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "varieties" in data
        assert "Red Wine" in data["varieties"]


class TestHealthAndRoot:
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "Wine API" in response.json()["message"]
