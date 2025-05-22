create table mcforumsearcher.public.forums(
	forum_id SERIAL primary key,
	forum_name TEXT,
	forum_name_slug VARCHAR(100),
	is_active INT default 0,
	url TEXT,
	category_id INT,
	constraint fk_category
	foreign key (category_id) references mcforumsearcher.public.categories(category_id)
);

create table mcforumsearcher.public.categories(
	category_id SERIAL primary key,
	category_name TEXT,
	category_name_slug VARCHAR(100),
	is_active INT default 0
);

insert into mcforumsearcher.public.forums (forum_name, forum_name_slug, url, category, is_active) values ('Donanım Haber Forum', 'donanimhaber', 'https://forum.donanimhaber.com/', 1, 1)
insert into mcforumsearcher.public.categories (category_name, category_name_slug, is_active) values ('Teknoloji', 'teknoloji', 1)