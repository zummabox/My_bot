from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm import joinedload

from database.models import Detail, Banner, Category


############### Работа с баннерами (информационными страницами) ###############

async def orm_add_banner_description(session: AsyncSession, data: dict):
    #Добавляем новый или изменяем существующий по именам
    query = select(Banner)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Banner(name=name, description=description) for name, description in data.items()])
    await session.commit()


async def orm_change_banner_image(session: AsyncSession, name: str, image: str):
    query = update(Banner).where(Banner.name == name).values(image=image)
    await session.execute(query)
    await session.commit()


async def orm_get_banner(session: AsyncSession, page: str):
    query = select(Banner).where(Banner.name == page)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_info_pages(session: AsyncSession):
    query = select(Banner)
    result = await session.execute(query)
    return result.scalars().all()


############################ Категории ######################################

async def orm_get_categories(session: AsyncSession):
    query = select(Category)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_create_categories(session: AsyncSession, categories: list):
    query = select(Category)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Category(name=name) for name in categories])
    await session.commit()


############ Админка: добавить/изменить/удалить товар ########################
async def orm_add_detail(session: AsyncSession, data: dict):
    obj = Detail(
        name=data["name"],
        number=data["number"],
        status=data["status"],
        category_id=int(data["category"]),
    )
    session.add(obj)
    await session.commit()


async def orm_get_details(session: AsyncSession, category_id):
    query = select(Detail).where(Detail.category_id == int(category_id))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_detail(session: AsyncSession, detail_id: int):
    query = select(Detail).where(Detail.id == detail_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_update_detail(session: AsyncSession, detail_id: int, data):
    query = (
        update(Detail)
        .where(Detail.id == detail_id)
        .values(
        name=data["name"],
        number=data["number"],
        status=data["status"],
    category_id=int(data["category"]),)
    )
    await session.execute(query)
    await session.commit()


async def orm_delete_detail(session: AsyncSession, detail_id: int):
    query = delete(Detail).where(Detail.id == detail_id)
    await session.execute(query)
    await session.commit()