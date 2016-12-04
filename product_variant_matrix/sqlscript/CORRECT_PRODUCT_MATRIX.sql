CREATE OR REPLACE FUNCTION correct_product_matrix(p_category_id integer)
  RETURNS boolean AS
$BODY$
DECLARE prod_temp_rec RECORD;
DECLARE prod_att_line_rec RECORD;
DECLARE att_line_ext_rec RECORD;
DECLARE  V_color_attribute_id INTEGER;
DECLARE V_size_attribute_id INTEGER;
DECLARE MAT_COLOR_REC RECORD;
DECLARE MAT_SIZE_REC RECORD;
DECLARE LAST_product_ID INTEGER;
BEGIN
  FOR prod_temp_rec IN SELECT ID AS PRODUCT_TEMP_ID ,CATEG_ID,name from product_template WHERE CATEG_ID=P_CATEGORY_ID
    LOOP
	-- Generate product_attribute_line
       For prod_att_line_rec IN Select A.product_tmpl_id,A.ID AS LINE_ID,B.ID AS VAL_ID 
				from product_attribute_line A,product_attribute_value B 
				where A.attribute_id=B.attribute_id AND A.product_tmpl_id=prod_temp_rec.PRODUCT_TEMP_ID
	Loop
		IF NOT exists(Select * FROM product_attribute_line_product_attribute_value_rel where line_id=prod_att_line_rec.line_id and val_id=prod_att_line_rec.val_id) THEN
			INSERT INTO product_attribute_line_product_attribute_value_rel(line_id,val_id) values(prod_att_line_rec.line_id,prod_att_line_rec.val_id);
		END IF;
	END LOOP;

	
	Select INTO  V_color_attribute_id,V_size_attribute_id DISTINCT color_attribute_id,size_attribute_id  from product_attribute_line_extend where product_tmp_id=prod_temp_rec.PRODUCT_TEMP_ID;
	FOR MAT_COLOR_REC IN Select COLOR_ID from product_category_attribure_color_rel WHERE category_id=P_CATEGORY_ID
	LOOP
	    FOR MAT_SIZE_REC IN Select SIZE_ID from product_category_attribure_size_rel WHERE category_id=P_CATEGORY_ID
	    LOOP
		IF NOT EXISTS(Select * from product_attribute_line_extend 
				Where product_tmp_id=prod_temp_rec.PRODUCT_TEMP_ID
				AND color_attribute_id=V_color_attribute_id
				AND color_value_id=MAT_COLOR_REC.COLOR_ID
				AND size_attribute_id=V_size_attribute_id
				AND size_value_id= MAT_SIZE_REC.SIZE_ID ) THEN
			INSERT INTO product_attribute_line_extend(product_tmp_id,size_attribute_id,size_value_id,color_attribute_id,color_value_id,is_active
			,create_uid,create_date,write_uid,write_date)
			VALUES (prod_temp_rec.PRODUCT_TEMP_ID,V_size_attribute_id,MAT_SIZE_REC.SIZE_ID,V_color_attribute_id,MAT_COLOR_REC.COLOR_ID,True
			,1,now(),1,now());
			
			INSERT INTO product_product(name_template, product_tmpl_id, active,create_uid,create_date,write_uid,write_date)
			    VALUES (prod_temp_rec.name,prod_temp_rec.PRODUCT_TEMP_ID,True,1,now(),1,now());
			
			SELECT currval(pg_get_serial_sequence('product_product', 'id')) INTO LAST_product_ID;

			INSERT INTo product_attribute_value_product_product_rel(att_id,prod_id)values(MAT_SIZE_REC.SIZE_ID,LAST_product_ID);
			INSERT INTo product_attribute_value_product_product_rel(att_id,prod_id)values(MAT_COLOR_REC.COLOR_ID,LAST_product_ID);
			
		END IF;
			
	    END LOOP;
	END LOOP;
    END LOOP;
    RETURN TRUE;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;