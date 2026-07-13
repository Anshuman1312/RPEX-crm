import csv
import io

from app.repositories.lead_repository import LeadRepository


class ReportService:
    def __init__(self, lead_repo: LeadRepository):
        self.lead_repo = lead_repo

    async def leads_csv_chunk(self, status: str | None = None):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "name", "email", "phone", "source", "status", "created_at"])
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)

        leads = await self.lead_repo.list_leads(skip=0, limit=100000, status=status)
        for lead in leads:
            writer.writerow([lead.id, lead.name, lead.email, lead.phone, lead.source, lead.status, lead.created_at])
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)
