#include <sddapi.h>

/****************************************************************************************
 * this file contains additional functions to the api for the sdd library
 ****************************************************************************************/

#ifndef SDDAPI_EXTRA_H_
#define SDDAPI_EXTRA_H_

void add_var_before_lca(int count, SddLiteral* literals, SddManager* manager);
void add_var_after_lca(int count, SddLiteral* literals, SddManager* manager);
void move_var_before_first(SddLiteral var, SddManager* manager);
void move_var_after_last(SddLiteral var, SddManager* manager);
void move_var_before(SddLiteral var, SddLiteral target_var, SddManager* manager);
void move_var_after(SddLiteral var, SddLiteral target_var, SddManager* manager);
void remove_var_added_last(SddManager*manager);

#endif // SDDAPI_EXTRA_H_

/****************************************************************************************
 * end
 ****************************************************************************************/
