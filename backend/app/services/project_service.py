from app.models.project import Project
from app.repositories.project_repository import ProjectRepository


class ProjectService:
    def __init__(self, repo: ProjectRepository):
        self.repo = repo

    async def create(self, payload: dict, user_id: str) -> Project:
        project = Project(**payload, created_by=user_id)
        return await self.repo.create(project)
